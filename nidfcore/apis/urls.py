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
    path('verifyotp/', views.VerifyOTPAPI.as_view(), name='verifyotp'),
]

# application (and associates) endpoints
urlpatterns += [
    path('applications/', views.ApplicationsAPIView.as_view(), name='applications'),
    path('repayments/', views.RepaymensAPIView.as_view(), name='repayments'),
    path('progressreports/', views.ProgressReportsAPIView.as_view(), name='progressreports'),
    path('disbursements/', views.DisbursementsAPIView.as_view(), name='disbursements'),
]


# dashboard
urlpatterns += [
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
]