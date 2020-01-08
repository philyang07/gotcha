from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player

# Register your models here.
class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Player'

class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)
    fieldsets = (
                    (
                        None, 
                        {'fields': ('username', 'first_name', 'last_name', 'email', 'password'), 
                        }
                    ),
                )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)