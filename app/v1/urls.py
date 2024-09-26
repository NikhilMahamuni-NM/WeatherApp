
from django.urls import path

from app.v1 import views

urlpatterns = [
    path('', views.home, name="home"),
    path('weather-results/', views.search, name="search_city")
]