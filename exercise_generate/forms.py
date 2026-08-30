from django import forms
from question.models import AnalysisBundle, AnalysisResult, PromptTemplate, Question


class Stage3RunForm(forms.Form):
    stage2_bundle = forms.ModelChoiceField(queryset=AnalysisBundle.objects.none())

    stage3_prompt = forms.ModelChoiceField(queryset=PromptTemplate.objects.filter(stage=PromptTemplate.STAGE_THREE).order_by('created_at'))

    question_bank_pdf = forms.FileField(label='PDF-file')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            self.fields['stage2_bundle'].queryset = AnalysisBundle.objects.filter(
                teacher=user,
                exam__teacher=user,
                stage=AnalysisBundle.STAGE_TWO,
                status=AnalysisBundle.STATUS_SUCCESS,
            ).order_by('-created_at')
