from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player
from django.urls import path
from django.http import HttpResponseRedirect

# Register your models here.
class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Player'

class UserAdmin(BaseUserAdmin):
    change_list_template = 'accounts/users_changelist.html'
    inlines = (PlayerInline,)
    fieldsets = (
                    (
                        None, 
                        {'fields': ('username', 'first_name', 'last_name', 'email', 'password'), 
                        }
                    ),
                )

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('reset_players/', self.reset_players)
        ]
        return extra_urls + urls

    def reset_players(self, request):
        Player.reset()
        self.message_user(request, "Resetted player codes, targets")
        return HttpResponseRedirect('../')
        
admin.site.unregister(User)
admin.site.register(User, UserAdmin)