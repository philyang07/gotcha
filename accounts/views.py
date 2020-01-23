from django.shortcuts import render, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Permission
from django.http import HttpResponseRedirect
from .forms import *
from django.contrib.auth.forms import PasswordResetForm
from .models import Player, Game
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import sys, os
from .tasks import *


# Create your views here.
def not_superuser(user):
    return not user.is_superuser
    
def populate_players(request):
    if request.method == "POST":
        game = Game.objects.get(pk=request.POST["pk"])
        game.populate_players()

    return HttpResponseRedirect(reverse("accounts:player_list"))

def default(request):
    if request.user.is_authenticated and not_superuser(request.user):
        return HttpResponseRedirect(reverse('accounts:profile'))
    return render(request, 'accounts/home.html')    

def guide(request):
    return render(request, 'accounts/guide.html')

def home_page(request):
    return render(request, 'accounts/home.html')

def login_view(request):
    """
    An experimental login view for learning's sake
    """
    form = BareLoginForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if request.user:
                logout(request)
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = BareLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def change_details(request):
    user = request.user
    form = None
    template = None
    initial = {'email': user.email}

    if request.user.has_perm("accounts.game_admin"):
        form = ChangeGameDetailsForm(request.POST, request=request)
        template = 'accounts/change_game_details.html'
        initial['open_duration'] = user.game.open_duration
        initial['respawn_time'] = user.game.respawn_time
        initial['max_players'] = user.game.max_players
        initial['access_code'] = user.game.access_code
        initial['rules'] = user.game.rules
        initial['target_assignment_time'] = user.game.target_assignment_time
        initial['start_elimination_time'] = user.game.start_elimination_time
        initial['game_end_time'] = user.game.game_end_time
    else:
        form = ChangePlayerDetailsForm(request.POST, request=request)
        template = 'accounts/change_player_details.html'
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        initial['death_message'] = user.player.death_message

    if request.method == "POST":
        if form.is_valid():
            if not request.user.has_perm("accounts.game_admin"):
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.player.death_message = form.cleaned_data['death_message']
                request.user.player.save()
            else:
                tat = form.cleaned_data['target_assignment_time']
                selt = form.cleaned_data['start_elimination_time']
                gendt = form.cleaned_data['game_end_time']
                resp = form.cleaned_data['respawn_time']
                game = request.user.game
                game.open_duration = form.cleaned_data['open_duration']
                game.access_code = form.cleaned_data['access_code']
                game.max_players = form.cleaned_data['max_players']
                game.rules = form.cleaned_data['rules']

                if resp != game.respawn_time or selt != game.start_elimination_time:
                    Task.objects.filter(task_name="accounts.tasks.respawn_players", creator_object_id=game.pk).delete()
                    Task.objects.filter(task_name="accounts.tasks.schedule_respawn", creator_object_id=game.pk).delete()
                    if resp > 0:
                        if selt: # if start elimination time specified
                            schedule_respawn(game.pk, resp, schedule=selt, creator=game)
                        elif game.in_elimination_stage:
                            respawn_players(game.pk, resp, repeat=30, repeat_until=game.game_end_time, creator=game)
                        elif game.winner or game.force_ended:
                            resp = 0

                if tat != game.target_assignment_time and tat:
                    # send_targets_and_codes.apply_async((game.pk, ), eta=tat)
                    send_targets_and_codes(game.pk, schedule=tat, creator=game)

                if selt != game.start_elimination_time and selt:
                    # start_elimination_round.apply_async((game.pk, ), eta=selt)
                    start_elimination_round(game.pk, schedule=selt, creator=game)
                
                if gendt != game.game_end_time and gendt:
                    end_game(game.pk, schedule=gendt, creator=game)

                game.target_assignment_time = tat
                game.start_elimination_time = selt
                game.game_end_time = gendt
                game.respawn_time = resp

                game.save()

            request.user.email = form.cleaned_data['email']
            request.user.username = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect(reverse('accounts:change_details'))
    else:
        if request.user.has_perm("accounts.game_admin"):
            form = ChangeGameDetailsForm(initial=initial, request=request)
        else:
            form = ChangePlayerDetailsForm(initial=initial, request=request)

    return render(request, template, {'form': form})

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")        
def rules(request):
    current_game = None
    if request.user.has_perm('accounts.game_admin'):
        current_game = Game.objects.get(admin=request.user)
    else:
        current_game = request.user.player.game    

    return render(request, 'accounts/rules.html', {'rules': current_game.rules})
    
    

def register(request):
    form = PlayerRegistrationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name'].lower().capitalize()
            last_name = form.cleaned_data['last_name'].lower().capitalize()
            user = User.objects.create_user(email, email, password, 
                                            first_name=first_name,
                                            last_name=last_name)
            user.player.game = Game.objects.get(access_code=form.cleaned_data['access_code'])
            user.player.alive = True
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
            user.user_permissions.add(Permission.objects.get(codename="game_admin"))
            game = Game(admin=user, access_code=Game.generate_access_code())
            game.save()
            login(request, user)

            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = RegistrationForm()

    return render(request, 'accounts/create_game.html', {'form': form})

def game_in_progress(user):
    if user.player.game: # user is a player
        return user.player.game.in_progress
    return not user.is_superuser and not user.game 

def complete_assignment(current_player, target_code):
    # regardless, the player submitting in the legit codes will get a kill
    game = current_player.game
    current_player.kills += 1
    current_player.manual_open = False

    """ 
    killing a player on the open list means
        1. the open player's original killer gets a new target; the open player's target 
    """
    open_codes = [p.secret_code for p in current_player.game.open_players()]

    # always prioritise actual target; or won't get credit for kill!
    if target_code == current_player.target.secret_code: # target is the actual target
        old_target = current_player.target
        if current_player == old_target.target:
            current_player.target = None
        else:
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

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def profile(request):
    if request.user.has_perm("accounts.game_admin"):
        return render(request, 'accounts/admin_dashboard.html', {'game': request.user.game})

    form = AssignmentForm(request.POST, request=request)
    if request.method == "POST":
        if form.is_valid():
            target_name = str(Player.objects.get(secret_code=form.cleaned_data['target_code']))
            complete_assignment(request.user.player, form.cleaned_data['target_code'])
            messages.add_message(request, messages.SUCCESS, "You successfully eliminated " + target_name + "!")
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = AssignmentForm()
    return render(request, 'accounts/profile.html', {'game': request.user.player.game, 'form': form,})

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))

@user_passes_test(game_in_progress, login_url="accounts:login")
@login_required(login_url="accounts:login")
def assignment(request):
    form = AssignmentForm(request.POST, request=request)
    if request.method == "POST":
        if form.is_valid():

            # regardless, the player submitting in the legit codes will get a kill
            current_player = request.user.player
            game = current_player.game
            current_player.kills += 1
            current_player.manual_open = False
            target_name = None

            """ 
            killing a player on the open list means
                1. the open player's original killer gets a new target; the open player's target 
            """
            open_codes = [p.secret_code for p in current_player.game.open_players()]
            target_code = form.cleaned_data['target_code']

            # always prioritise actual target; or won't get credit for kill!
            if target_code == current_player.target.secret_code: # target is the actual target
                old_target = current_player.target
                target_name = str(old_target)
                if current_player == old_target.target:
                    current_player.target = None
                else:
                    current_player.target = old_target.target
                old_target.alive = False
                old_target.target = None
                current_player.last_active = old_target.last_active = timezone.now()
                old_target.save()
                current_player.save()
            else: # open otherwise
                open_player = Player.objects.get(game=game, secret_code=target_code)
                target_name = str(open_player)
                open_player_killer = Player.objects.get(game=game, target__secret_code=target_code)
                open_player_killer.target = open_player.target
                open_player.target = None
                open_player.alive = False
                current_player.last_active = open_player.last_active = timezone.now()
                current_player.save()
                open_player.save()
                open_player_killer.save()
            messages.add_message(request, messages.SUCCESS, "You successfully eliminated " + target_name + "!")
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = AssignmentForm()
    return render(request, 'accounts/profile.html', {'form': form})

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def player_list(request):
    template_name = current_game = None

    if request.user.has_perm('accounts.game_admin'):
        current_game = Game.objects.get(admin=request.user)
        template_name = 'accounts/admin_player_list.html'
    else:
        current_game = request.user.player.game
        template_name = 'accounts/player_list.html'

    players = current_game.players().filter(secret_code__isnull=False).order_by('-alive', '-kills', '-last_active') 
    new_players = current_game.players().filter(secret_code__isnull=True)

    max_kills = most_kills_players = None
    if players:
        max_kills = max([p.kills for p in players])
        if max_kills > 0:
            most_kills_players = [p for p in current_game.players().filter(secret_code__isnull=False) if p.kills == max_kills]

    context = {
        'game': current_game,
        'players': players,
        'max_kills': max_kills, 
        'most_kills_players': most_kills_players,
        'new_players': new_players, 
        'target_ordering': current_game.target_ordering(),
    }

    if settings.DEBUG:
        context['DEBUG'] = True

    return render(request, template_name, context)


@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def graveyard(request):
    template_name = 'accounts/graveyard.html'
    
    current_game = None
    if request.user.has_perm('accounts.game_admin'):
        current_game = Game.objects.get(admin=request.user)
    else:
        current_game = request.user.player.game
    
    dead_players = current_game.players().filter(alive=False, secret_code__isnull=False).order_by('-last_active')

    context = {
        'dead_players': dead_players
    }

    return render(request, template_name, context)





@login_required(login_url="accounts:login")
def delete_player(request):
    game = None
    if request.user.has_perm("accounts.game_admin"):
        game = request.user.game
    else:
        game = request.user.player.game

    if request.method == "POST": # must be by game admin
        player = None
        if Player.objects.get(pk=request.POST["pk"]):
            player = Player.objects.get(pk=request.POST["pk"])
        else:
            return HttpResponseRedirect(reverse('accounts:player_list'))
        player.manual_delete()
        messages.add_message(request, messages.INFO, 'Deleted ' + str(player))
    else:
        if not request.user.has_perm("accounts.game_admin"):
            request.user.player.manual_delete()
            messages.add_message(request, messages.INFO, 'Your account was deleted')
            logout(request)
    if not game.players().filter(secret_code__isnull=False) and not game.in_registration: # if this deletes the last player of the game, run it back to the start!
        game.in_progress = False
        game.save()
        messages.add_message(request, messages.INFO, 'The last player was deleted so the game was reset back to registration')
    if not request.user.has_perm('accounts.game_admin'):
        return HttpResponseRedirect(reverse('accounts:home'))
    return HttpResponseRedirect(reverse('accounts:player_list'))
    

    

@login_required(login_url="accounts:login")
def manual_open(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect(reverse('accounts:player_list'))
        player = Player.objects.get(pk=request.POST["pk"])
        if player.manual_open:
            player.manual_open = False
            messages.add_message(request, messages.INFO, 'Set ' + str(player) + " to not manually open")
        else:
            player.manual_open = True
            messages.add_message(request, messages.INFO, 'Set ' + str(player) + " to manually open")
        player.save()
        return HttpResponseRedirect(reverse('accounts:player_list'))
    return HttpResponseRedirect(reverse('accounts:login'))

@user_passes_test(not_superuser, login_url="accounts:login")
@login_required(login_url="accounts:login")
def manual_kill(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect(reverse('accounts:player_list'))
        player = Player.objects.get(pk=request.POST["pk"])
        if not player.alive:
            player.manual_add()
            messages.add_message(request, messages.INFO, 'Revived ' + str(player) + " with random target")
        else:
            player.manual_kill()
            messages.add_message(request, messages.INFO, 'Manually killed ' + str(player))
    else:
        if not request.user.has_perm("accounts.game_admin"):
            request.user.player.manual_kill()

    if request.user.has_perm("accounts.game_admin"):
        return HttpResponseRedirect(reverse('accounts:player_list'))
    return HttpResponseRedirect(reverse('accounts:profile'))

@login_required(login_url="accounts:login")
def manual_add(request):
    if request.method == "POST":
        if not Player.objects.filter(pk=request.POST["pk"]):
            return HttpResponseRedirect(reverse('accounts:player_list'))
        player = Player.objects.get(pk=request.POST["pk"])
        player.manual_add()
        messages.add_message(request, messages.INFO, "Added " + str(player) + " into the arena")
    if request.user.has_perm("accounts.game_admin"):
        return HttpResponseRedirect(reverse('accounts:player_list'))
    return HttpResponseRedirect(reverse('accounts:profile'))

@login_required(login_url="accounts:login")
def reset_player_data(request):
    if request.POST.get('reset'):
        request.user.game.reset()
        messages.add_message(request, messages.INFO, "Reset players' kills and targets")
    else:
        if len(request.user.game.players()) < 2:
            messages.add_message(request, messages.INFO, "Can't assign targets with less than two players!")
            return HttpResponseRedirect(reverse('accounts:profile'))
        elif not request.user.game.in_registration:
            if request.user.game.in_target_sending:
                messages.add_message(request, messages.INFO, "Already assigned targets!")
            return HttpResponseRedirect(reverse('accounts:player_list'))               
        else:
            request.user.game.reset()
            request.user.game.target_assignment_time = None
            messages.add_message(request, messages.INFO, 'Sent targets to players')
    return HttpResponseRedirect(reverse('accounts:player_list'))

@login_required(login_url="accounts:login")
def delete_game(request):
    request.user.game.delete_game()
    messages.add_message(request, messages.INFO, 'Game deleted')
    return HttpResponseRedirect(reverse('accounts:login'))

@login_required(login_url="accounts:login")
def force_end_game(request):
    if request.method == "POST":
        request.user.game.force_ended = True
        request.user.game.save()
        messages.add_message(request, messages.INFO, 'Game has been force ended')
    return HttpResponseRedirect(reverse('accounts:profile'))

@login_required(login_url="accounts:login")
def reset_game_to_start(request):
    if request.method == "POST":
        request.user.game.reset(to_start=True)
        messages.add_message(request, messages.INFO, 'Reset back to registration stage')
    return HttpResponseRedirect(reverse('accounts:player_list'))

@login_required(login_url="accounts:login")
def reassign_targets(request):
    messages.add_message(request, messages.INFO, 'Reassigned targets')
    request.user.game.reassign_targets()
    return HttpResponseRedirect(reverse('accounts:player_list'))

@login_required(login_url="accounts:login")
def start_game(request):
    game = request.user.game

    if not game.in_target_sending:
        if game.in_elimination_stage:
            messages.add_message(request, messages.INFO, "Already started game!")
        return HttpResponseRedirect(reverse('accounts:player_list'))
    
    if len(game.players().filter(secret_code__isnull=False)) < 2:
        messages.add_message(request, messages.WARNING, "Can only start a game with 2 players or more!")
        return HttpResponseRedirect(reverse('accounts:profile'))

    game.in_progress = True
    if game.respawn_time > 0:
        respawn_players(game.pk, game.respawn_time, repeat=30, repeat_until=game.game_end_time, creator=game)
    
    game.start_elimination_time = None
    game.save()

    for player in game.players().filter(secret_code__isnull=False):
        player.last_active = timezone.now()
        player.save()

    messages.add_message(request, messages.INFO, 'Elimination stage has begun')
    return HttpResponseRedirect(reverse('accounts:player_list'))