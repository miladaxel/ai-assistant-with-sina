from django.urls import path
from .views import Stage2RunView, Stage2StudentDetailView, Stage2ResultsView
from analysis import views
app_name = 'analysis'

urlpatterns = [
    path('stage2/run/', Stage2RunView.as_view(), name='stage2_run'),
    path('stage2/result/<int:exam_id>/',Stage2ResultsView.as_view(), name='stage2_result'),
    path('stage2/bundle/<int:pk>/', Stage2StudentDetailView.as_view(), name='stage2_student_detail'),
    path('teacher_note/', views.TeacherNote.as_view(), name='teacher_note'),
    path('weekly_plan/', views.WeeklyPlan.as_view(), name='weekly_plan'),
    path('settings/', views.Settings.as_view(), name='settings'),
    path('messenger/', views.Messenger.as_view(), name='messenger'),
    path('exam_step1', views.ExamStep1.as_view(), name='exam_step1'),
    path('exam_step2', views.ExamStep2.as_view(), name='exam_step2'),
    path('choose_school/', views.ChooseSchool.as_view(), name='choose_school'),
    path('exam_management/', views.ExamManagement.as_view(), name='exam_management'),
    path('choose_class/', views.ChooseClass.as_view(), name='choose_class'),
    path('pre_analyze/', views.PreAnalysisResult.as_view(), name='pre_analyze'),
    path('pre_analyze_list/', views.PreAnalysisResultList.as_view(), name='pre_analyze_list')

]

