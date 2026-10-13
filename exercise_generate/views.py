from django.db import transaction

from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, DetailView

from exercise_generate.forms import Stage3RunForm
from question.models import AnalysisBundle, AnalysisResult
from question.tasks import process_analysis_bundle
from question.services.background import enqueue_after_commit
from question.mixins import TeacherRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from ai_asistant_with_sina.query_cache import CachedBundleDetailMixin, CachedListMixin


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

        with transaction.atomic():
            bundle = AnalysisBundle.objects.create(
                title=f"تمرین | {stage2_bundle.title}"[:120],
                exam_id=stage2_bundle.exam_id,
                teacher=self.request.user,
                prompt_template=stage3_prompt,
                stage=AnalysisBundle.STAGE_THREE,
                model_name="gpt-4.1-mini",
                status=AnalysisBundle.STATUS_PENDING,
                lesson_pdf=uploaded_pdf,
                input_json={
                    "STAGE2_JSON": stage2_bundle.result.result_json,
                    "STAGE2_BUNDLE_ID": stage2_bundle.pk,
                },
            )
            enqueue_after_commit(process_analysis_bundle, bundle)

        return redirect("exercise_generate:stage3_detail", pk=bundle.pk)


class Stage3StudentListView(LoginRequiredMixin, TeacherRequiredMixin, CachedListMixin, ListView):
    template_name = 'exercise_generate/stage3_list.html'
    context_object_name = 'bundles'
    paginate_by = 20

    def get_queryset(self):
        return (
            AnalysisBundle.objects.filter(
                teacher=self.request.user,
                exam__teacher=self.request.user,
                stage=AnalysisBundle.STAGE_THREE,
            ).defer("input_json").order_by('-created_at', '-pk')
        )


class AnalysisBundleDetailViewStage3(LoginRequiredMixin, TeacherRequiredMixin, CachedBundleDetailMixin, DetailView):
    model = AnalysisBundle
    template_name = "exercise_generate/bundle_detail_stage3.html"
    context_object_name = "bundle"

    def get_queryset(self):
        return AnalysisBundle.objects.filter(
            teacher=self.request.user,
            exam__teacher=self.request.user,
            stage=AnalysisBundle.STAGE_THREE,
        ).select_related("result")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = getattr(self.object, "result", None)
        context['result'] = (
            result if result and result.stage == AnalysisResult.STAGE_THREE else None
        )
        return context
