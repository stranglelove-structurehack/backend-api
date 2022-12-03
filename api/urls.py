from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
	path('', views.welcome, name = 'welcome'),
	
	path('register', views.RegisterView.as_view(), name="registration"),
	path('login', views.LoginView.as_view(), name="login"),
	path('logout', views.LogoutView.as_view(), name="logout"),
	path('user/get', views.UserGetView.as_view()),
]