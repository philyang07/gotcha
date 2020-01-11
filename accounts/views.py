from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.http import HttpResponseRedirect
from .forms import AssignmentForm, PlayerRegistrationForm, RegistrationForm
from .models import Player, Game
from datetime import timedelta
from django.utils import timezone

# Create your views here.
def register(request):
    if request.method == "GET":
        for game in Game.objects.all():
            for i in range(5):
                email = Game.generate_access_code() + "@gmail.com"
                first_name = Game.generate_access_code().lower()
                last_name = Game.generate_access_code().lower()

                user = User.objects.create_user(email, email, 123, 
                                        first_name=first_name,
                                        last_name=last_name)
                user.save()
                user.player.game = game
                user.player.alive = True
                user.player.save()
    return HttpResponseRedirect(reverse("accounts:login"))

# def register(request):
#     form = PlayerRegistrationForm(request.POST)
#     if request.method == "POST":
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password1']
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             user = User.objects.create_user(email, email, password, 
#                                             first_name=first_name,
#                                             last_name=last_name)
#             user.player.game = Game.objects.get(access_code=form.cleaned_data['access_code'])
#             user.player.save()
            
#             login(request, user)
#             return HttpResponseRedirect(reverse('accounts:profile'))
#     else:
#         form = PlayerRegistrationForm()

#     return render(request, 'accounts/register.html', {'form': form})

def create_game(request):
    form = RegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(email, email, password)
            user.user_permissions.add(Permission.objects.get(codename="game_admin"))
            game = Game(admin=user, access_code=Game.generate_access_code())
            game.save()
            login(request, user)

            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = RegistrationForm()

    return render(request, 'accounts/create_game.html', {'form': form})

@login_required(login_url="accounts:login")
def profile(request):
    if request.user.has_perm("accounts.game_admin"):
        return render(request, 'accounts/admin_dashboard.html')
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

            # regardless, the player submitting in the legit codes will get a kill
            current_player = request.user.player
            game = current_player.game
            current_player.kills += 1

            """ 
            killing a player on the open list means
                1. the open player's original killer gets a new target; the open player's target 
            """
            open_codes = [p.secret_code for p in current_player.game.open_players()]
            target_code = form.cleaned_data['target_code']

            # always prioritise actual target; or won't get credit for kill!
            if target_code == current_player.target.secret_code: # target is the actual target
                old_target = current_player.target
                current_player.target = old_target.target
                old_target.alive = False
                old_target.target = None
                current_player.last_active = old_target.last_active = timezone.now()
                old_target.save()
                current_player.save()
            else: # open otherwise
                open_player = Player.objects.get(game=game, secret_code=target_code)
                open_player_killer = Player.objects.get(game=game, target__secret_code=target_code)
                open_player_killer.target = open_player.target
                open_player.target = None
                open_player.alive = False
                current_player.last_active = open_player.last_active = timezone.now()
                current_player.save()
                open_player.save()
                open_player_killer.save()

            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = AssignmentForm()
    return render(request, 'accounts/assignment.html', {'form': form})

@login_required(login_url="accounts:login")
def player_list(request):
    template_name = current_game = None

    if request.user.has_perm('accounts.game_admin'):
        current_game = Game.objects.get(admin=request.user)
        template_name = 'accounts/admin_player_list.html'
    else:
        current_game = request.user.player.game
        template_name = 'accounts/player_list.html'

    all_players = current_game.players().order_by('-alive', '-kills', '-last_active') 
    new_players = current_game.players().filter(last_active__isnull=True)

    context = {
        'players': all_players,
        'new_players': new_players, 
        'target_ordering': current_game.target_ordering(),
    }

    return render(request, template_name, context)

@login_required(login_url="accounts:login")
def delete_player(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect('/accounts/players')
        player = Player.objects.get(pk=request.POST["pk"])
        player.manual_delete()

    if request.user.has_perm("accounts.game_admin"):
        return HttpResponseRedirect('/accounts/players')
    return HttpResponseRedirect('/accounts/login')

@login_required(login_url="accounts:login")
def manual_open(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect('/accounts/players')
        player = Player.objects.get(pk=request.POST["pk"])
        if player.manual_open:
            player.manual_open = False
        else:
            player.manual_open = True
        player.save()
        return HttpResponseRedirect('/accounts/players')
    return HttpResponseRedirect("/accounts/login")

@login_required(login_url="accounts:login")
def manual_kill(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect('/accounts/players')
        player = Player.objects.get(pk=request.POST["pk"])
        player.manual_kill()
    if request.user.has_perm("accounts.game_admin"):
        return HttpResponseRedirect('/accounts/players')
    return HttpResponseRedirect('/accounts/profile')

@login_required(login_url="accounts:login")
def reset_player_data(request):
    request.user.game.reset()
    return HttpResponseRedirect('/accounts/players') 

@login_required(login_url="accounts:login")
def reassign_targets(request):
    request.user.game.reassign_targets()
    return HttpResponseRedirect('/accounts/players') 