from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='crime_report/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='crime_report/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='crime_report/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='crime_report/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='crime_report/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='crime_report/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='crime_report/password_change.html'),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='crime_report/password_change_done.html'),
         name='password_change_done'),
    
    # Crime reports
    path('report/', views.report_crime, name='report_crime'),
    path('crimes/', views.CrimeListView.as_view(), name='crime_list'),
    path('crime/<int:pk>/', views.CrimeDetailView.as_view(), name='crime_detail'),
    
    # Admin/Police dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-reports/', views.manage_reports, name='manage_reports'),
    path('update-report/<int:pk>/', views.update_report_status, name='update_report_status'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('update-user-type/<int:pk>/', views.update_user_type, name='update_user_type'),
    
    # API
    path('api/crime-stats/', views.crime_stats_api, name='crime_stats_api'),
]