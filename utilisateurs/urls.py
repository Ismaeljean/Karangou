from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('inscription/complete/', views.complete_profile, name='complete_profile'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/realisations/', views.mes_realisations, name='mes_realisations'),
    path('profile/projets/', views.mes_projets, name='mes_projets'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
