from django.urls import path
from . import views

urlpatterns = [
    path('login_user/', views.MyView.login_user, name='login'),
    path('register_user/', views.MyView.register_user, name='register'),
    path('logout_user/', views.MyView.logout_user, name='logout'),
    path('send_friend_request/', views.MyView.send_friend_request, name='send_request'),
    path('accept_friend_request/', views.MyView.accept_friend_request, name='accept_request'),
    path('reject_friend_request/', views.MyView.reject_friend_request, name='reject_request'),
    path('get_friends/', views.MyView.get_friends, name='get_friends'),
    path('get_friend_requests/', views.MyView.get_friend_requests, name='get_friend_requests'),
    path('view_friend_status/', views.MyView.view_friend_status, name='friendship_status'),
    path('remove_friend/', views.MyView.remove_friend, name='remove_friend'),
]