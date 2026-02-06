from django.urls import path
from .views import Stage2RunView, Stage2StudentDetailView, Stage2ResultsView

app_name = 'analysis'

urlpatterns = [
    path('stage2/run/', Stage2RunView.as_view(), name='stage2_run'),
    path('stage2/result/<int:exam_id>/',Stage2ResultsView.as_view(), name='stage2_result'),
    path('stage2/bundle/<int:pk>/', Stage2StudentDetailView.as_view(), name='stage2_student_detail')
]

