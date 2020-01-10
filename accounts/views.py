from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import AssignmentForm, PlayerRegistrationForm, RegistrationForm
from .models import Player, Game
from datetime import timedelta
from django.utils import timezone

# Create your views here.
def register(request):
    form = PlayerRegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User.objects.create_user(email, email, password, 
                                            first_name=first_name,
                                            last_name=last_name)
            user.player.game = Game.objects.get(access_code=form.cleaned_data['access_code'])
            user.player.save()
            
            login(request, user)
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = PlayerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def create_game(request):
    form = RegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(email, email, password)
            game = Game(admin=user, access_code=Game.generate_access_code())
            game.save()
            login(request, user)

            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = RegistrationForm()

    return render(request, 'accounts/create_game.html', {'form': form})

@login_required(login_url="accounts:login")
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'accounts/profile.html')

@login_required(login_url="accounts:login")
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))

@login_required(login_url="accounts:login")
def assignment(request):
    form = AssignmentForm(request.POST, request=request)
    if request.method == "POST":
        if form.is_valid():
            current_player = request.user.player
            current_player.kills += 1
            old_target = current_player.target
            current_player.target = old_target.target
            old_target.alive = False
            old_target.target = None
            current_player.last_active = old_target.last_active = timezone.now()
            old_target.save()
            current_player.save()

            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = AssignmentForm()
    return render(request, 'accounts/assignment.html', {'form': form})

def player_list(request):
    template_name = 'accounts/player_list.html'

    current_game = None
    if Game.objects.get(admin=request.user):
        current_game = Game.objects.get(admin=request.user)
    else:
        current_game = request.user.player.game

    all_players = Player.objects.filter(user__is_staff=False, game=current_game).order_by('-kills', '-last_active')

    context = {
        'players': all_players,
        'target_ordering': Player.target_ordering(current_game),
        }

    return render(request, template_name, context)
