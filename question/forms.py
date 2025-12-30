from symtable import Class

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

class QuestionHasSubForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['has_subquestion']


QuestionHasSubFormSet = modelformset_factory(Question, form=QuestionHasSubForm, extra=0)


class QuestionSubCountForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subquestion_count']

    def clean_subquestion_count(self):
        val = self.cleaned_data.get('subquestion_count')
        if val is None:
            return 0
        if val < 0:
            raise forms.ValidationError('Subquestion count must be non-negative')
        return val

QuestionSubCountFormSet = modelformset_factory(Question, form=QuestionSubCountForm, extra=0)

class ExamStudentForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='انتخاب دانش‌آموزان'
    )

    def __init__(self, *args, **kwargs):
        student_qs = kwargs.pop('students_qs')
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = student_qs