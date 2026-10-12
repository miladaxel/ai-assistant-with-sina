from django.contrib import admin
from .models import PromptTemplate, AnalysisBundle, AnalysisResult, Exam, Question, SubQuestion, ExamParticipation, \
    StudentQuestionResult, ExamSnapShot


class RelatedQuestionAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if field is not None:
            if db_field.remote_field.model is Question:
                field.queryset = field.queryset.select_related("exam")
            elif db_field.remote_field.model is SubQuestion:
                field.queryset = field.queryset.select_related("question__exam")
        return field

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'created_at')
    list_filter = ('is_active', 'stage','created_at')
    search_fields = ('name',)

class AnalysisResultInline(admin.StackedInline):
    model = AnalysisResult
    extra = 0
    can_delete = True
    fields = ('stage', 'result_json', 'raw_output_text', 'openai_response_id', 'usage_json')
    readonly_fields = ('created_at',)

@admin.register(AnalysisBundle)
class AnalysisBundleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status','model_name', 'created_at')
    list_filter = ('status', 'model_name','stage', 'created_at')
    search_fields = ('title',)
    inlines = [AnalysisResultInline]

    def has_result(self, obj):
        return hasattr(obj, 'result')
    has_result.boolean = True
    has_result.short_description = 'result?'

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_filter = ('stage','created_at')
    list_display = ('id', 'bundle', 'created_at', 'stage', 'created_at', 'bundle_id')
    autocomplete_fields = ('bundle',)


class ExamParticipationInline(admin.TabularInline):
    model = ExamParticipation
    extra = 0
    autocomplete_fields = ['student']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("student", "exam")

@admin.register(ExamParticipation)
class ExamParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'exam')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'total_question', 'created_at')
    search_fields = ('name', 'teacher__username')
    inlines = [ExamParticipationInline]

@admin.register(Question)
class QuestionAdmin(RelatedQuestionAdmin):
    list_display = ('id', 'exam', 'number', 'has_subquestion', 'subquestion_count')
    list_select_related = ('exam',)

@admin.register(SubQuestion)
class SubQuestionAdmin(RelatedQuestionAdmin):
    list_display = ('id', 'question', 'number')
    list_select_related = ('question__exam',)


@admin.register(StudentQuestionResult)
class StudentQuestionResultAdmin(RelatedQuestionAdmin):
    list_display = ('id', 'exam', 'student', 'question', 'subquestion', 'is_correct')
    list_select_related = ('exam', 'student', 'question__exam', 'subquestion__question__exam')


@admin.register(ExamSnapShot)
class ExamSnapShotAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'created_at')
    list_select_related = ('exam',)
