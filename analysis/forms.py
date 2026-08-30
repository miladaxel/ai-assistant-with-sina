from django import forms
from question.models import Exam, PromptTemplate


class Stage2RunForm(forms.Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.none(), required=True)
    stage1_bundle_id = forms.IntegerField(required=True)
    stage2_prompt = forms.ModelChoiceField(
        queryset=PromptTemplate.objects.filter(is_active=True, stage=PromptTemplate.STAGE_TWO).order_by("name", "-version"),
        required=True
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            self.fields["exam"].queryset = Exam.objects.filter(
                teacher=user
            ).order_by("-created_at")
