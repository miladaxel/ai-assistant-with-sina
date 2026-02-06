from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.db import transaction
from django.urls import reverse
from .forms import Stage2RunForm
from question.models import AnalysisBundle, AnalysisResult, ExamSnapShot, Exam, PromptTemplate
from .services.stage2 import fill_stage2_prompt
from question.services.openai_client import OpenAIAnalyzer
from Profile.models import Student
import json
from django import forms
from question.models import ExamSnapShot  # مسیر را مچ کن

class Stage2RunView(FormView):
    template_name = "analysis/stage2_run.html"
    form_class = Stage2RunForm

    def _get_exam_id_from_request(self):
        return self.request.GET.get("exam") or self.request.POST.get("exam")

    def _get_stage1_bundles_for_exam(self, exam_id):
        qs = AnalysisBundle.objects.filter(status=AnalysisBundle.STATUS_SUCCESS).order_by("-created_at")
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        return qs.select_related("prompt_template", "exam")[:300]

    def _fill_stage2_prompt(self, template_text: str, *, exam_map_json: dict, student_answers: dict) -> str:
        return (
            template_text
            .replace("{{EXAM_MAP_JSON}}", json.dumps(exam_map_json, ensure_ascii=False))
            .replace("{{STUDENT_ANSWERS}}", json.dumps(student_answers, ensure_ascii=False))
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        exam_id = self._get_exam_id_from_request()
        ctx["selected_exam_id"] = exam_id

        ctx["stage1_bundles"] = self._get_stage1_bundles_for_exam(exam_id)

        snapshot_info = None
        if exam_id:
            snap = ExamSnapShot.objects.filter(exam_id=exam_id).order_by("-created_at").first()
            if snap:
                data = snap.data or {}
                students = data.get("students", []) or []
                snapshot_info = {
                    "exists": True,
                    "snapshot_id": snap.id,
                    "created_at": snap.created_at,
                    "student_count": len(students),
                }
            else:
                snapshot_info = {"exists": False}

        ctx["snapshot_info"] = snapshot_info
        return ctx

    def form_invalid(self, form):
        messages.error(self.request, "فرم خطا دارد. موارد را بررسی کن.")
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        exam = form.cleaned_data["exam"]
        stage1_bundle_id = form.cleaned_data["stage1_bundle_id"]
        stage2_prompt = form.cleaned_data["stage2_prompt"]

        stage1_bundle = (
            AnalysisBundle.objects
            .select_related("exam")
            .filter(id=stage1_bundle_id, status=AnalysisBundle.STATUS_SUCCESS)
            .first()
        )
        if not stage1_bundle:
            messages.error(self.request, "خروجی Stage1 معتبر نیست یا success نیست.")
            return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")

        if stage1_bundle.exam_id and stage1_bundle.exam_id != exam.id:
            messages.error(self.request, "خروجی Stage1 انتخابی مربوط به این Exam نیست.")
            return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")

        if not hasattr(stage1_bundle, "result"):
            messages.error(self.request, "Stage1 bundle انتخابی result ندارد.")
            return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")

        exam_map_json = stage1_bundle.result.result_json

        snapshot_obj = ExamSnapShot.objects.filter(exam=exam).order_by("-created_at").first()
        if not snapshot_obj:
            messages.error(self.request, "برای این Exam هیچ Snapshot پیدا نشد.")
            return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")

        snapshot = snapshot_obj.data or {}
        students_payloads = snapshot.get("students", []) or []
        if not students_payloads:
            messages.error(self.request, "Snapshot انتخابی دانش‌آموزی ندارد.")
            return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")

        analyzer = OpenAIAnalyzer()
        ok, bad = 0, 0
        for sp in students_payloads:
            student_id = sp.get("student_id")
            full_name = sp.get("full_name") or ""

            if not student_id:
                bad += 1
                continue

            input_json = {
                "EXAM_MAP_JSON": exam_map_json,
                "STUDENT_ANSWERS": sp,
                "STAGE1_BUNDLE_ID": stage1_bundle.id,
                "SNAPSHOT_ID": snapshot_obj.id,
            }

            with transaction.atomic():
                bundle = AnalysisBundle.objects.create(
                    title=f"Stage2 | Exam {exam.id} | Student {student_id} - {full_name}",
                    teacher=self.request.user,
                    prompt_template=stage2_prompt,
                    model_name="gpt-4o-mini",
                    status=AnalysisBundle.STATUS_PENDING,
                    stage="stage2_student_diagnosis",
                    exam=exam,
                    input_json=input_json,
                )

                try:
                    prompt_text = self._fill_stage2_prompt(
                        stage2_prompt.instruction_text,
                        exam_map_json=exam_map_json,
                        student_answers=sp,
                    )
                    print('step1')
                    resp = analyzer.analyze_text(model=bundle.model_name, prompt_text=prompt_text)
                    print("========= raw model output=========")
                    print(resp.raw_output_text)
                    print("====================================")
                    AnalysisResult.objects.create(
                        bundle=bundle,
                        result_json=resp.parsed_json,
                        raw_output_text=resp.raw_output_text,
                        openai_response_id=resp.response_id,
                        usage_json=resp.usage,
                    )

                    bundle.status = AnalysisBundle.STATUS_SUCCESS
                    bundle.save(update_fields=["status"])
                    ok += 1
                except Exception as e:
                    bundle.status = AnalysisBundle.STATUS_FAILURE
                    bundle.error_message = str(e)
                    bundle.save(update_fields=["status", "error_message"])
                    bad += 1

        messages.success(self.request, f"Stage2 تمام شد. موفق: {ok} | ناموفق: {bad}")
        return redirect(f"{reverse('analysis:stage2_run')}?exam={exam.id}")



class Stage2ResultsView(ListView):
    template_name = "analysis/stage2_results.html"
    context_object_name = "bundles"

    def get_queryset(self):
        exam_id = self.kwargs["exam_id"]
        return (
            AnalysisBundle.objects
            .filter(exam_id=exam_id, stage="stage2_student_diagnosis")
            .select_related("prompt_template", "exam")
            .order_by("-created_at")
        )


class Stage2StudentDetailView(DetailView):
    model = AnalysisBundle
    template_name = "analysis/stage2_student_detail.html"
    context_object_name = "bundle"

    def get_queryset(self):
        return AnalysisBundle.objects.select_related("result", "prompt_template", "exam", "teacher")