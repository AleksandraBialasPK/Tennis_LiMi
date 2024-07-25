from django.urls import include, path
from . import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', logout_then_login, name='logout'),
    path('day/', views.DayView.as_view(), name='day'),
    path('week/', views.WeekView.as_view(), name='week'),
    path("select2/", include("django_select2.urls")),
    # path('getEventsForDay/', views.GetEventsForDayView.as_view(), name='get_events_for_day'),
]