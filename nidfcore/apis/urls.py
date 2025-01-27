from django.urls import path

from . import views

app_name = 'apis'

urlpatterns = [
    path('', views.PingAPI.as_view(), name='ping'),
]