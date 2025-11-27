from django.urls import path
from Profile import views

urlpatterns = [
    path('upload_exel/', views.ExcelUploadView.as_view(), name='upload_exel'),
    path('upload_success/', views.SuccessView.as_view(), name='upload_success'),
]