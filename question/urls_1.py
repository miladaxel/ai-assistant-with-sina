from django.urls import path
from question import views

urlpatterns = [
    path('', views.ChatTestView.as_view(), name='chat_test'),
    path('exam/', views.ExamQuestionListView.as_view(), name='exam_question_list'),
    path('analyze/', views.AnalyzeStudentsView.as_view(), name='text_analyze'),
    path('assignment/', views.AssignExercisesView.as_view(), name='assignment_question_list'),
]