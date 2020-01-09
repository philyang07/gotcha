from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import RegistrationForm, AssignmentForm
from .models import Player
from datetime import timedelta
from django.utils import timezone

# Create your views here.
def register(request):
    form = RegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

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

    open_players = Player.objects.filter(last_active__lte=timezone.now() - timedelta(hours=24))
    all_players = Player.objects.filter(user__is_staff=False).order_by('-kills', '-last_active')

    context = {
        'players': all_players,
        'target_ordering': Player.target_ordering(),
        }

    return render(request, template_name, context)
