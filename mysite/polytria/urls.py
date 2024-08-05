from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='polytria-home'),
    path('about/', views.about, name='polytria-about'),
    path('result/', views.result, name='polytria-result'),
]