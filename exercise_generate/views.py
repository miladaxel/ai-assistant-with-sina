import tempfile
import os

from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, DetailView

from exercise_generate.forms import Stage3RunForm
from question.models import AnalysisBundle, AnalysisResult
from question.services.openai_client import OpenAIAnalyzer
import json
from question.mixins import TeacherRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class Stage3RunView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    template_name = "exercise_generate/stage3_run.html"
    form_class = Stage3RunForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        stage2_bundle = form.cleaned_data["stage2_bundle"]
        stage3_prompt = form.cleaned_data["stage3_prompt"]
        uploaded_pdf = form.cleaned_data["question_bank_pdf"]

        analyzer = OpenAIAnalyzer()
        analyzer.__init__()

        # ===== ذخیره موقت فایل PDF =====
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in uploaded_pdf.chunks():
                temp_file.write(chunk)
            temp_pdf_path = temp_file.name

        try:
            # ===== آپلود به OpenAI =====
            pdf_file_id = analyzer.upload_pdf(temp_pdf_path)

            # ===== خروجی Stage2 =====
            stage2_json = stage2_bundle.result.result_json

            # ===== ساخت دستورالعمل (instructions) =====
            instructions = stage3_prompt.instruction_text.replace(
                "{{STAGE2_JSON}}",
                json.dumps(stage2_json, ensure_ascii=False)
            )

            # ===== اسکیما =====
            json_schema = stage3_prompt.schema_json or {}

            # (اختیاری ولی بهتر) اگر اسکیما خالی بود، جلوی اجرا را بگیر
            if not json_schema:
                raise ValueError("Stage3 prompt schema_json is empty. Please set schema_json for this template.")

            # ===== اجرای مدل با فایل + اسکیما (STRICT) =====
            resp = analyzer.analyze(
                model='gpt-4.1-mini',
                instructions=instructions,
                json_schema=json_schema,
                textbook_file_id=pdf_file_id,  # همان فایل
                exam_file_id=pdf_file_id,      # همان فایل (minimal-change)
                temperature=0.2,

            )

            # ===== ذخیره Bundle =====
            bundle = AnalysisBundle.objects.create(
                exam=stage2_bundle.exam,
                teacher=self.request.user,
                prompt_template=stage3_prompt,
                stage=AnalysisBundle.STAGE_THREE,
                status=AnalysisBundle.STATUS_SUCCESS,

                # پیشنهاد: برای ردیابی
                openai_lesson_file_id=pdf_file_id,
                openai_example_file_id=pdf_file_id,
            )

            # ===== ذخیره نتیجه =====
            AnalysisResult.objects.create(
                bundle=bundle,
                result_json=resp.parsed_json,
                raw_output_text=resp.raw_output_text,
                openai_response_id=resp.response_id,
                usage_json=resp.usage,
                # اگر stage را در Result نگه می‌داری
                stage=AnalysisResult.STAGE_THREE,
            )

        finally:
            # پاک کردن فایل موقت
            try:
                os.remove(temp_pdf_path)
            except Exception:
                pass

        return redirect("exercise_generate:stage3_detail", pk=bundle.pk)


class Stage3StudentListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    template_name = 'exercise_generate/stage3_list.html'
    context_object_name = 'bundles'

    def get_queryset(self):
        return (
            AnalysisBundle.objects.filter(
                teacher=self.request.user,
                exam__teacher=self.request.user,
                stage=AnalysisBundle.STAGE_THREE,
            ).order_by('-created_at')
        )


class AnalysisBundleDetailViewStage3(LoginRequiredMixin, TeacherRequiredMixin ,DetailView):
    model = AnalysisBundle
    template_name = "exercise_generate/bundle_detail_stage3.html"
    context_object_name = "bundle"

    def get_queryset(self):
        return AnalysisBundle.objects.filter(
            teacher=self.request.user,
            exam__teacher=self.request.user,
            stage=AnalysisBundle.STAGE_THREE,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = AnalysisResult.objects.filter(
            bundle=self.object,
            stage=AnalysisResult.STAGE_THREE
        ).first()
        return context
