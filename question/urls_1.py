from django.urls import path
from question import views

urlpatterns = [
    path('', views.ChatTestView.as_view(), name='chat_test'),
    path('exam/', views.ExamQuestionListView.as_view(), name='exam_question_list'),
    path('analyze/', views.AnalyzeStudentsView.as_view(), name='text_analyze'),
    path('assignment/', views.AssignExercisesView.as_view(), name='assignment_question_list'),
    path('bundles/new/', views.AnalysisBundleCreateView.as_view(), name='bundle_create'),
    path('bundles/<int:pk>/', views.AnalysisBundleDetailView.as_view(), name='bundle_detail'),
    path('bundles/mine/', views.MyAnalysisBundlesView.as_view(), name='my_bundles'),
    path('exam/create', views.ExamCreateView.as_view(), name='exam_create'),
    path('exam/<int:exam_id>/setup/', views.ExamQuestionsSetupView.as_view(), name='exam_question_setup'),
    path('exam/<int:exam_id>/subquestions/', views.ExamSubQuestionsSetupView.as_view(), name='exam_sub_question_setup'),
    path('exam/<int:exam_id>/summary/', views.ExamSummaryView.as_view(), name='exam_summary'),
    path('exam/<int:exam_id>/students/', views.ExamSelectStudentsView.as_view(), name='exam_select_students'),
    path('exam/<int:exam_id>/corroct/<int:student_id>/', views.ExamCorrectionView.as_view(), name='exam_correction'),
    path('exam/<int:exam_id>/results/',views.ExamResultsReportView.as_view(),name='exam_results_report'),
    path('exam/<int:exam_id>/snapshot/create/',views.ExamSnapShotCreateView.as_view(),name='exam_snapshot_create'),
    path('exam/<int:exam_id>/snapshots/',views.ExamSnapShotListView.as_view(),name='exam_snapshot_list'),
    path('exam/participation_list/<int:exam_id>/', views.StudentParticipationListView.as_view(), name='exam_participation_list'),

]