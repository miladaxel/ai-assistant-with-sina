from symtable import Class

from .models import AnalysisBundle, PromptTemplate, Exam, Question, StudentQuestionResult
from django import forms
from django.forms import BaseModelFormSet, modelformset_factory
from .models import StudentQuestionResult
from ai_asistant_with_sina.query_cache import CachedPromptChoiceField


class AnalysisBundleCreateForm(forms.ModelForm):
    prompt_template = CachedPromptChoiceField(
        cache_variant='stage1-active-name-version',
        queryset=PromptTemplate.objects.filter(is_active=True, stage=PromptTemplate.STAGE_ONE).order_by(
            'name', '-version'),
        empty_label='یک پرامپت را انتخاب کنید',
        label='پرامپت تحلیل',
        required=True
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.none(), label='ازمون',
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            self.fields['exam'].queryset = Exam.objects.filter(
                teacher=user
            ).order_by('-created_at')

    class Meta:
        model = AnalysisBundle
        fields = ['title', 'lesson_pdf', 'example_pdf', 'prompt_template', 'exam']



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


class CachedQuestionChoiceField(forms.ModelChoiceField):
    """Validate hidden IDs using the formset's already scoped, loaded questions."""

    def __init__(self, *args, instances, **kwargs):
        self.instances = instances
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        self.validate_no_null_characters(value)
        try:
            if isinstance(value, Question):
                value = value.pk
            return self.instances[Question._meta.pk.to_python(value)]
        except (KeyError, ValueError, TypeError, forms.ValidationError):
            raise forms.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice", params={"value": value},
            )


class BaseQuestionFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if not hasattr(self, "_question_instances"):
            self._question_instances = {question.pk: question for question in self.get_queryset()}
        original = form.fields["id"]
        form.fields["id"] = CachedQuestionChoiceField(
            queryset=self.get_queryset(), instances=self._question_instances,
            initial=original.initial, required=original.required, widget=original.widget,
        )


QuestionHasSubFormSet = modelformset_factory(
    Question, form=QuestionHasSubForm, formset=BaseQuestionFormSet, extra=0,
)


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

QuestionSubCountFormSet = modelformset_factory(
    Question, form=QuestionSubCountForm, formset=BaseQuestionFormSet, extra=0,
)

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





class StudentQuestionResultForm(forms.ModelForm):
    # فقط یک Checkbox ساده
    is_correct = forms.BooleanField(
        required=False,
        label='درست است؟'
    )

    class Meta:
        model = StudentQuestionResult
        fields = ('is_correct',)



StudentQuestionResultFormSet = modelformset_factory(StudentQuestionResult, form=StudentQuestionResultForm, extra=0)
