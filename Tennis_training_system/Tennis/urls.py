from django.urls import path
from . import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', logout_then_login, name='logout'),
    path('day/', views.day, name='day'),
    path('week/', views.week, name='week'),
]