from django import forms
from question.models import Exam, PromptTemplate


class Stage2RunForm(forms.Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.all(), required=True)
    stage1_bundle_id = forms.IntegerField(required=True)
    stage2_prompt = forms.ModelChoiceField(
        queryset=PromptTemplate.objects.filter(is_active=True).order_by("name", "-version"),
        required=True
    )