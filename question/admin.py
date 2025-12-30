from django.contrib import admin
from .models import PromptTemplate, AnalysisBundle, AnalysisResult, Exam, Question, SubQuestion, ExamParticipation

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)

@admin.register(AnalysisBundle)
class AnalysisBundleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status','model_name', 'created_at')
    list_filter = ('status', 'model_name')
    search_fields = ('title',)

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'bundle', 'created_at')

class ExamParticipationInline(admin.TabularInline):
    model = ExamParticipation
    extra = 0
    autocomplete_fields = ['student']

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





