from django.urls import path, reverse_lazy
from .forms import PickyAuthenticationForm
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=PickyAuthenticationForm), name='login'),
    path('', views.login_view, name='login'), 
    path('login/', views.login_view, name='login'), # for learning's sake
    path('register/', views.register, name='register'),
    path('populate_players/', views.populate_players, name="populate_players"),
    path('create_game/', views.create_game, name="create_game"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logout, name="logout"),
    path('assignment/', views.assignment, name="assignment"),
    path('change_details/', views.change_details, name="change_details"),
    path('graveyard/', views.graveyard, name="graveyard"),
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


    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change_form.html",
        success_url=reverse_lazy("accounts:password_change_done")
    ), name="password_change"),

    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html"
    ), name="password_change_done"),

    # password reset urls
    path('password_reset/', auth_views.PasswordResetView.as_view(
        email_template_name="accounts/password_reset_email.html",
        template_name="accounts/password_reset_form.html",
        success_url=reverse_lazy("accounts:password_reset_done")
    ), name="password_reset"),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"
    ), name="password_reset_done"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete")
    ), name="password_reset_confirm"),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"
    ), name="password_reset_complete"),
]
