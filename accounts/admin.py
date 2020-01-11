from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player, Game
from django.urls import path
from django.http import HttpResponseRedirect

# Register your models here.
class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Player'
    template = "accounts/player_inline.html"

class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)

    # fieldsets = (
    #                 (
    #                     None, 
    #                     {'fields': ('first_name', 'last_name', 'email', 'password'), 
    #                     }
    #                 ),
    #             )

    # add_fieldsets = (
    #     (None, {
    #         'fields': ('first_name', 'last_name', 'email', 'password1', 'password2')

    #     }),
    # )

    def save_model(self, request, obj, form, change):
        obj.username = form.cleaned_data['email']
        super().save_model(request, obj, form, change)


class GameAdmin(admin.ModelAdmin):
    inlines = (PlayerInline, ) 

    change_form_template = 'accounts/game_change_form.html'
    
    def get_urls(self):
        urls = super(GameAdmin, self).get_urls()
        extra_urls = [
            path('<int:pk>/change/reset_players/', self.reset_players),
            path('<int:pk>/change/reassign_targets/', self.reassign_targets),
            path('<int:pk>/change/manual_kill/', self.manual_kill),
            path('<int:pk>/change/manual_delete/', self.manual_delete),
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
        if player.manual_kill():
            self.message_user(request, player_name + " is already eliminated. No changes made.")
        else:
            self.message_user(request, "Manually killed player " + player_name)
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

# class PlayerAdmin(admin.ModelAdmin):
#     change_form_template = 'accounts/player_change_form.html'
    
#     def get_urls(self):
#         urls = super(PlayerAdmin, self).get_urls()
#         extra_urls = [
#             path('<int:pk>/change/manual_kill/', self.manual_kill),
#             path('<int:pk>/change/manual_delete/', self.manual_delete),
#         ]
#         return extra_urls + urls

#     def manual_kill(self, request, **kwargs):
#         if request.method == "GET":
#             self.message_user(request, "Didn't kill as wasn't via button")
#             return HttpResponseRedirect('../')
#         Player.objects.get(pk=kwargs['pk']).manual_kill()

#         self.message_user(request, "Manually killed player")
#         return HttpResponseRedirect('../')

#     def manual_delete(self, request, **kwargs):
#         if request.method == "GET":
#             self.message_user(request, "Didn't delete as wasn't via button")
#             return HttpResponseRedirect('../')
#         Player.objects.get(pk=kwargs['pk']).manual_delete()

#         self.message_user(request, "Manually deleted player")
#         return HttpResponseRedirect('/admin/accounts/player')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player)