from django.urls import path

from . import views

app_name = 'apis'

# ping api endpoint
urlpatterns = [
    path('', views.PingAPI.as_view(), name='ping'),
]   

# auth api endpoints
urlpatterns += [
    path('login/', views.LoginAPI.as_view(), name='login'),
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('logout/', views.LogoutAPI.as_view(), name='logout'),
]