from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'chat'

urlpatterns = [
    path('chat/', views.home, name='home'),
    path('chat/archive/', views.archive, name='archive'),
    path('chat/room/<int:pk>/', views.room_detail, name='room'),
    path('chat/create-room/', views.create_room, name='create_room'),
    path('chat/room-update/<int:pk>/', views.update_room, name='update_room'),
    path('chat/delete/<int:pk>/', views.delete_room, name='delete_room'),
    path('chat/edit-message/<int:pk>/', views.edit_message, name='edit_message'),
    path('chat/delete-message/<int:pk>/', views.delete_message, name='delete_message'),
    path('chat/topics/', views.topics, name='topics'),
    path('chat/activity/', views.activity, name='activity'),
    path('chat/profile/<int:pk>/', views.profile, name='profile'),
    path('chat/edit-profile/', views.edit_profile, name='edit_profile'),

    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='chat/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
