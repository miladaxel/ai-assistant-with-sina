import tempfile

from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, DetailView

from exercise_generate.forms import Stage3RunForm
from question.models import AnalysisBundle, AnalysisResult
from question.services.openai_client import OpenAIAnalyzer
import json
from question.mixins import TeacherRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class Stage3RunView(FormView):
    template_name = "exercise_generate/stage3_run.html"
    form_class = Stage3RunForm

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

        # ===== آپلود به OpenAI =====
        pdf_file_id = analyzer.upload_pdf(temp_pdf_path)

        # ===== خروجی Stage2 =====
        stage2_json = stage2_bundle.result.result_json

        # ===== ساخت پرامپت =====
        prompt_text = stage3_prompt.instruction_text.replace(
            "{{STAGE2_JSON}}",
            json.dumps(stage2_json, ensure_ascii=False)
        )

        # ===== اجرای مدل =====
        resp = analyzer.analyze_text(
            model='gpt-4o-mini',
            prompt_text=prompt_text,
        )
        print('======================================')
        print(resp.raw_output_text)

        # ===== ذخیره Bundle =====
        bundle = AnalysisBundle.objects.create(
            exam=stage2_bundle.exam,
            teacher=self.request.user,
            prompt_template=stage3_prompt,
            stage=AnalysisBundle.STAGE_THREE,
            status=AnalysisBundle.STATUS_SUCCESS,
        )

        # ===== ذخیره نتیجه =====
        AnalysisResult.objects.create(
            bundle=bundle,
            result_json=resp.parsed_json,
            raw_output_text=resp.raw_output_text,
            openai_response_id=resp.response_id,
            usage_json=resp.usage,
            stage=AnalysisResult.STAGE_THREE,
        )

        return redirect(
            "home",
            exam_id=bundle.exam.id
        )


class Stage3StudentListView(ListView):
    template_name = 'exercise_generate/stage3_list.html'
    context_object_name = 'bundles'

    def get_queryset(self):
        return (
            AnalysisBundle.objects.filter(
                teacher=self.request.user, stage=AnalysisBundle.STAGE_THREE
            ).order_by('-created_at')
        )


class AnalysisBundleDetailViewStage3(LoginRequiredMixin, TeacherRequiredMixin ,DetailView):
    model = AnalysisBundle
    template_name = "exercise_generate/bundle_detail_stage3.html"
    context_object_name = "bundle"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = AnalysisResult.objects.filter(
            bundle=self.object,
            stage=AnalysisResult.STAGE_THREE
        ).first()
        return context