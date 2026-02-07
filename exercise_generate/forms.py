from django import forms
from question.models import AnalysisBundle, AnalysisResult, PromptTemplate, Question


class Stage3RunForm(forms.Form):
    stage2_bundle = forms.ModelChoiceField(queryset=AnalysisBundle.objects.filter(stage=AnalysisBundle.STAGE_TWO).order_by('created_at'))

    stage3_prompt = forms.ModelChoiceField(queryset=PromptTemplate.objects.filter(stage=PromptTemplate.STAGE_THREE).order_by('created_at'))

    question_bank_pdf = forms.FileField(label='PDF-file')