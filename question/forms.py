from django import forms
from .models import AnalysisBundle, PromptTemplate

class AnalysisBundleCreateForm(forms.ModelForm):
    prompt_template = forms.ModelChoiceField(
        queryset=PromptTemplate.objects.filter(is_active=True).order_by(
            'name', '-version'),
        empty_label='یک پرامپت را انتخاب کنید',
        label='پرامپت تحلیل',
        required=True
    )


    class Meta:
        model = AnalysisBundle
        fields = ['title', 'lesson_pdf', 'example_pdf', 'prompt_template']