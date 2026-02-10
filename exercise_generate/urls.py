from django.urls import path
from exercise_generate import views

app_name = 'exercise_generate'

urlpatterns = [
    path('', views.Stage3RunView.as_view(), name='stage3_run'),
    path('stage3_list/', views.Stage3StudentListView.as_view(), name='stage3_list'),
    path('stage3/<int:pk>/',views.AnalysisBundleDetailViewStage3.as_view(),name='stage3_detail'),

]