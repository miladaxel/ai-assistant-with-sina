from django.contrib import admin
from .models import PromptTemplate, AnalysisBundle, AnalysisResult, Exam, Question, SubQuestion, ExamParticipation, \
    StudentQuestionResult, ExamSnapShot

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

@admin.register(ExamParticipation)
class ExamParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'exam')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'total_question', 'created_at')
    search_fields = ('name', 'teacher__username')
    inlines = [ExamParticipationInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass

@admin.register(SubQuestion)
class SubQuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(StudentQuestionResult)
class StudentQuestionResultAdmin(admin.ModelAdmin):
    pass


@admin.register(ExamSnapShot)
class ExamSnapShotAdmin(admin.ModelAdmin):
    pass