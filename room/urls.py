from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.process_league, name='leaguehq-home'),
    path('', views.process_league),
]
