from django import forms
from .models import AnalysisBundle

class AnalysisBundleCreateForm(forms.ModelForm):
    class Meta:
        model = AnalysisBundle
        fields = ['title', 'lesson_pdf', 'example_pdf']