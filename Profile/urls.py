from django.urls import path
from Profile import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('upload_exel/', views.ExcelUploadView.as_view(), name='upload_exel'),
    path('upload_success/', views.SuccessView.as_view(), name='upload_success'),
    # path('login/', views.StudentLoginView.as_view(), name='student_login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('panel/', views.StuedentPanelView.as_view(), name='panel'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]