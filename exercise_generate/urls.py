from django.urls import path
from exercise_generate import views

app_name = 'exercise_generate'

urlpatterns = [
    path('', views.Stage3RunView.as_view(), name='stage3_run'),

]