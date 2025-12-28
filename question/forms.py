from django import forms
from .models import AnalysisBundle, PromptTemplate, Exam, Question
from django.forms import modelformset_factory


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



class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'total_question']

    def clean_total_question(self):
        n = self.cleaned_data['total_question']
        if n < 1 or n > 300 :
            raise forms.ValidationError('question must be between 1 and 300')
        return n

QuestionSetupFormSet = modelformset_factory(
    Question,
    fields=('has_subquestion', 'subquestion_count'),
    extra=0,
    can_delete=False
)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam', 'number', 'has_subquestion', 'subquestion_count']

    def clean_subquestion_count(self):
        count = self.cleaned_data['subquestion_count']
        if count < 0 :
            raise forms.ValidationError('Subquestion count must positive.')
        return count
