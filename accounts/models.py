from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint, choice
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from datetime import timedelta
import string

# Create your models here.
class GamePlayerManager(models.Manager):
    use_for_related_fields = True
    def query_set(self):
        return super().get_queryset().filter()


class Game(models.Model):
    access_code = models.CharField('access_code', max_length=4, unique=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    
    class Meta:
        permissions = [
            ("game_admin", "Can view game statistics"),
        ]

    def players(self):
        return self.player_set.filter(game=self).exclude(Q(user__user_permissions__codename="accounts.game_admin"))

    def generate_access_code():
        existing_access_codes = [g.access_code for g in Game.objects.all()]
        candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        while candidate_code in existing_access_codes:
            candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        return candidate_code

    def __str__(self):
        return self.access_code + " - " + self.admin.email

    def reset(self): # reset codes, 
        players = self.players()

        for player in players:
            player.last_active = timezone.now()
            player.kills = 0
            player.manual_open = False
            player.alive = True
            player.save()

        for player in players:
            candidate_code = randint(100, 999)

            while players.filter(secret_code=candidate_code):
                candidate_code = randint(100, 999)
            player.secret_code = candidate_code

            player.save()

        self.reassign_targets()

    def reassign_targets(self):
        players = self.players().filter(alive=True)

        if not players:
            return

        for player in players:
            player.target = None
            player.save()


        # target assignment process:
        # 1. choose a random player to be the 'first' target
        # 2. choose another player without a target, that isn't the first target
        # 3. set this player's target to the 'first' target
        # 4. select another player with no target, and set their target to be the last player to be assigned a target
        # 5. repeat step 4 until all players apart from the 'first' target have a target
        # 6. set the first player's target to the last player to have a target assigned to them

        if len(players) == 1:
            return

        first_target = last_target = choice(players)
        last_killer = choice(players.filter(target=None).exclude(pk=first_target.pk))
        while players.filter(target=None).exclude(pk=first_target.pk):
            last_killer.target = last_target
            last_killer.save()
            last_target = last_killer
            if players.filter(target=None).exclude(pk=first_target.pk):
                last_killer = choice(players.filter(target=None).exclude(pk=first_target.pk))
        first_target.target = last_killer
        first_target.save()

    def open_players(self):
        return [p for p in self.players() if p.is_open]

    def target_ordering(self):
        players = self.players().filter(alive=True, target__isnull=False)
        if not players:
            return None
        counted_players = [players[0]]
        while len(counted_players) < len(players):
            counted_players.append(counted_players[-1].target)
        
        return " -->\n".join([str(counted_players.index(p)+1) + ". " + str(p) for p in counted_players]) + " -->"

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_code = models.IntegerField('secret code', null=True, blank=True)
    target = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    alive = models.BooleanField('alive', default=False)
    last_active = models.DateTimeField('last active', null=True, blank=True) # the last time the player eliminated someone
    kills = models.IntegerField('eliminations', default=0, null=True, blank=True)
    manual_open = models.BooleanField('manual open', default=False)

    class Meta:
        unique_together = ('game', 'secret_code',)


    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return self.user.first_name + " " + self.user.last_name
        return "player " + str(self.pk) + " " + self.user.email

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        if not Player.objects.filter(user=instance) and not instance.has_perm("accounts.game_admin"):
            player = Player(user=instance)
            player.save()
            instance.player = player

    @property
    def inactivity_duration(self):
        if not self.last_active:
            return "Not in game"
    

        duration = timezone.now() - self.last_active
        minutes = int(divmod(duration.total_seconds(), 3600)[1]/60)
        hours = int(duration.total_seconds()/3600)
        hr_str = "hr" if hours == 1 else "hrs"
        min_str = "min" if minutes == 1 else "mins"
        if not self.alive:
            return f"Dead for {hours} {hr_str}, {minutes} {min_str}"
        return f"{hours} {hr_str}, {minutes} {min_str}"

    @property
    def is_open(self):
        if not self.last_active:
            return None
        return self.alive and (self.manual_open or timezone.now() - self.last_active > timedelta(hours=24))

    def manual_delete(self):
        player = self
        player_user = player.user
        if Player.objects.filter(target=player):
            player_killer = Player.objects.get(target=player)
            player_killer.target = player.target
            player.target = None
            player.save()
            player_killer.save()
            player.delete()
        player_user.delete()     

    def manual_kill(self):
        player = self
        if Player.objects.filter(target=player): # equivalent them to being alive
            player_killer = Player.objects.get(target=player)
            player_killer.target = player.target
            player.target = None
            player.last_active = timezone.now()
            player.alive = False
            player.save()
            player_killer.save()   
        else:
            return True
