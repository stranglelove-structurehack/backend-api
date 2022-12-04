from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
	path('', views.welcome, name = 'welcome'),
	
	path('register', views.RegisterView.as_view(), name="registration"),
	path('login', views.LoginView.as_view(), name="login"),
	path('logout', views.LogoutView.as_view(), name="logout"),
	
	path('user/get', views.UserGetView.as_view()),
	path('user/subscribe_to', views.SubscribeView.as_view()),
	path('user/subscribers_list', views.SubscribersListView.as_view()),
	path('user/subscription_list', views.SubscriptionListView.as_view()),
	
	path("materials/get_from_user", views.GetFromUserMaterialsView.as_view()),
	path("materials/create", views.CreateMaterialView.as_view()),
]