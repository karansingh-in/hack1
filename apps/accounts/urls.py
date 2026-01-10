from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.dummy, name='login'),
    path('register/', views.dummy, name='register'),
]
