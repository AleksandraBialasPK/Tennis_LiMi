from django.urls import path
from . import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', logout_then_login, name='logout'),
    path('day/', views.DayView.as_view(), name='day'),
    path('add_event/', views.CreateEventView.as_view(), name='add_event'),
    path('week/', views.WeekView.as_view(), name='week'),
    # path('getEventsForDay/', views.GetEventsForDayView.as_view(), name='get_events_for_day'),
]