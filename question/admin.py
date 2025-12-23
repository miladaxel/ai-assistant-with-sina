from django.contrib import admin
from .models import PromptTemplate, AnalysisBundle, AnalysisResult

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

