from django.urls import path

from . import views

app_name = 'apis'

# ping api endpoint
urlpatterns = [
    path('', views.PingAPI.as_view(), name='ping'),
]   

# auth and user api endpoints
urlpatterns += [
    path('login/', views.LoginAPI.as_view(), name='login'),
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('logout/', views.LogoutAPI.as_view(), name='logout'),
    path('users/', views.UsersAPIView.as_view(), name='users'),
    path('userprofile/', views.UserProfileAPIView.as_view(), name='userprofile'),
    path('verifyotp/', views.VerifyOTPAPI.as_view(), name='verifyotp'),
]

# application (and associates) endpoints
urlpatterns += [
    path('applications/', views.ApplicationsAPIView.as_view(), name='applications'),
    path('process-application/', views.ProcessApplicationsAPIView.as_view(), name='process_app'),
    path('extra-application-info/', views.AdditionalInformationAPIView.as_view(), name='extra_info'),
]

# reports and repayments
urlpatterns += [
    path('repayments/', views.RepaymensAPIView.as_view(), name='repayments'),
    path('verifyrepayments/', views.VerifyRepaymentAPIView.as_view(), name='verify_repayments'),
    path('progressreports/', views.ProgressReportsAPIView.as_view(), name='progressreports'),
    path('verifyreports/', views.VerifyProgressReportAPIView.as_view(), name='verify_reports'),
]

# disbursements
urlpatterns += [
    path('disbursements/', views.DisbursementsAPIView.as_view(), name='disbursements'),
]

# dashboard
urlpatterns += [
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
]

# church and divisions endpoints
urlpatterns += [
    path('churches/', views.ChurchesAPIView.as_view(), name='churches'),
    path('regions/', views.RegionsAPIView.as_view(), name='regions'),
    path('divisions/', views.DivisionsAPIView.as_view(), name='districts'),
]

# notifications endpoints
urlpatterns += [
    path('notifications/', views.NotificationsAPIView.as_view(), name='notifications'),
    # broadcast scheduled notifications
    path('broadcastsn/', views.ScheduledNotificationBroadcastAPIView.as_view(), name='bsn'),
]