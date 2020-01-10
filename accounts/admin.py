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

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player)