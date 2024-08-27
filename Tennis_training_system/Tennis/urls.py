from django.urls import include, path
from . import views
from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', logout_then_login, name='logout'),
    path('day/', views.DayView.as_view(), name='day'),
    path('week/', views.WeekView.as_view(), name='week'),
    path('profile/', views.UsersProfile.as_view(), name='users_profile'),
    path("select2/", include("django_select2.urls")),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)