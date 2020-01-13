from django.urls import path
from .forms import PickyAuthenticationForm
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=PickyAuthenticationForm), name='login'),
    path('login/', views.login_view, name='login'), # for learning's sake
    path('register/', views.register, name='register'),
    path('populate_players/', views.populate_players, name="populate_players"),
    path('create_game/', views.create_game, name="create_game"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logout, name="logout"),
    path('assignment/', views.assignment, name="assignment"),
    path('players/', views.player_list, name="player_list"),
    path('delete_player/', views.delete_player, name="delete_player"),
    path('manual_open/', views.manual_open, name="manual_open"),
    path('manual_kill/', views.manual_kill, name="manual_kill"),
    path('manual_add/', views.manual_add, name="manual_add"),
    path('reset_player_data/', views.reset_player_data, name="reset_player_data"),
    path('reassign_targets/', views.reassign_targets, name="reassign_targets"),
    path('start_game/', views.start_game, name="start_game"),
    path('delete_game/', views.delete_game, name="delete_game"),
    path('reset_game_to_start/', views.reset_game_to_start, name="reset_game_to_start"),
]
