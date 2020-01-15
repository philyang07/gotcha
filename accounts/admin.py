from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player, Game
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.exceptions import ValidationError
from .forms import CustomUserChangeForm

# Register your models here.
class PlayerInline(admin.TabularInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Player'
    # template = "accounts/player_inline.html"
    template = "accounts/player_tabular_inline.html"
    extra = 0

    raw_id_fields =  ['user']

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm


    def save_model(self, request, obj, form, change):
        email = form.cleaned_data['email'].lower()
        if not obj.is_superuser:
            obj.username = form.cleaned_data['email']
        super().save_model(request, obj, form, change)


class GameAdmin(admin.ModelAdmin):
    inlines = (PlayerInline, ) 

    change_form_template = 'accounts/game_change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        game = Game.objects.get(pk=object_id)
        players = game.players().filter(secret_code__isnull=False).order_by('-alive', '-kills', '-last_active') 
        new_players = game.players().filter(secret_code__isnull=True)

        extra_context = {
            'game': game,
            'players': players,
            'new_players': new_players,
        }

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def get_urls(self):
        urls = super(GameAdmin, self).get_urls()
        extra_urls = [
            path('<int:pk>/change/reset_players/', self.reset_players),
            path('<int:pk>/change/start_game/', self.start_game),
            path('<int:pk>/change/reset_game_to_start/', self.reset_game_to_start),
            path('<int:pk>/change/delete_game/', self.delete_game),
            path('<int:pk>/change/populate_players/', self.populate_players),
            path('<int:pk>/change/reassign_targets/', self.reassign_targets),
            path('<int:pk>/change/manual_kill/', self.manual_kill),
            path('<int:pk>/change/manual_delete/', self.manual_delete),
            path('<int:pk>/change/manual_add/', self.manual_add),
        ]
        return extra_urls + urls

    def reset_players(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't reset as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game.reset()
        self.message_user(request, "Resetted player codes, targets")
        return HttpResponseRedirect('../')

    def delete_game(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't delete as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game_name = str(current_game)
        current_game.delete_game()
        self.message_user(request, "Deleted game " + current_game_name)
        return HttpResponseRedirect('/admin/accounts/game')

    def reset_game_to_start(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't start game as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game.reset(to_start=True)

        self.message_user(request, "Started a new game")
        return HttpResponseRedirect('../')

    def start_game(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't reset game as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game.in_progress = True
        for player in current_game.players().filter(secret_code__isnull=False):
            player.last_active = timezone.now()
            player.save()

        current_game.save()

        self.message_user(request, "Started game")
        return HttpResponseRedirect('../')

    def populate_players(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't do anything as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game.populate_players()

        self.message_user(request, "Added extra randoms into the game")
        return HttpResponseRedirect('../')

    def reassign_targets(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't reassign as wasn't via button")
            return HttpResponseRedirect('../')
        current_game = Game.objects.get(pk=kwargs['pk'])
        current_game.reassign_targets()
        self.message_user(request, "Reassigned targets")
        return HttpResponseRedirect('../')

    def manual_kill(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't kill as wasn't via button")
            return HttpResponseRedirect('../')

        player = Player.objects.get(pk=request.POST['player_pk'])
        player_name = str(player)
        
        if not player.alive:
            player.manual_add()
        else:
            if player.manual_kill():
                if player.game.winner:
                    self.message_user(request, player_name + " is the winner. No changes made.")
                else:
                    self.message_user(request, player_name + " is already eliminated. No changes made.")
            else:
                self.message_user(request, "Manually killed player " + player_name)
        return HttpResponseRedirect('../')

    def manual_add(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't add as wasn't via button")
            return HttpResponseRedirect('../')
        player = Player.objects.get(pk=request.POST['player_pk'])
        player_name = str(player)
        player.manual_add()

        self.message_user(request, "Manually added player " + player_name + " to the game")
        return HttpResponseRedirect('../')

    def manual_delete(self, request, **kwargs):
        if request.method == "GET":
            self.message_user(request, "Didn't delete as wasn't via button")
            return HttpResponseRedirect('../')
        player = Player.objects.get(pk=request.POST['player_pk'])
        player_name = str(player)
        player.manual_delete()

        self.message_user(request, "Manually deleted player " + player_name)
        return HttpResponseRedirect('../')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('game', 'get_name', 'user',)

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    get_name.short_description = 'Player name'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)