# fit_app/urls.py

from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('authorize/', views.authorize, name='authorize'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('fit_data/', views.get_fit_data, name='get_fit_data'),
    path('bmi/', views.bmi, name='bmi'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('heartpredict/', views.heartpredict, name='heartpredict'),
    path('tracking/', views.tracking, name='tracking'),
]
