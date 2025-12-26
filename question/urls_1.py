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
]