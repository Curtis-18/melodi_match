# genreprediction/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('predict/', views.predict_genre, name='predict'),  # This is your 'predict' view
    path('logout/', views.logout_view, name='logout'),
    
]
