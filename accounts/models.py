from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint, choice
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
import string

# Create your models here.
class Game(models.Model):
    access_code = models.CharField('access_code', max_length=4, unique=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def generate_access_code():
        existing_access_codes = [g.access_code for g in Game.objects.all()]
        candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        while candidate_code in existing_access_codes:
            candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        return candidate_code

    def __str__(self):
        return self.access_code + " - " + self.admin.email

    def reset(self): # reset codes, 
        # clear everything
        players = Player.objects.filter(game=self, user__is_staff=False)

        if not players:
            return

        for user in [player.user for player in players]:
            user.player.delete()
            Player(game=self, user=user).save()

        players = Player.objects.filter(game=self, user__is_staff=False)
        
        for player in players:
            player.last_active = timezone.now()
            candidate_code = randint(100, 999)

            while Player.objects.filter(game=self, secret_code=candidate_code):
                candidate_code = randint(100, 999)
            player.secret_code = candidate_code

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
        last_killer = choice(Player.objects.filter(game=self, target=None).exclude(pk=first_target.pk))
        while Player.objects.filter(game=self, target=None).exclude(pk=first_target.pk):
            last_killer.target = last_target
            last_killer.save()
            last_target = last_killer
            if Player.objects.filter(game=self, target=None).exclude(pk=first_target.pk):
                last_killer = choice(Player.objects.filter(game=self, target=None).exclude(pk=first_target.pk))
        first_target.target = last_killer
        first_target.save()

    def target_ordering(self):
        players = Player.objects.filter(game=self, user__is_staff=False, alive=True)
        if not players:
            return None
        counted_players = [players[0]]
        while len(counted_players) < len(players):
            counted_players.append(counted_players[-1].target)
        
        return " -->\n".join([str(counted_players.index(p)+1) + ". " + str(p) for p in counted_players]) + " -->"

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_code = models.IntegerField('secret code', null=True, blank=True, unique=True)
    target = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    alive = models.BooleanField('alive', default=False)
    last_active = models.DateTimeField('last active', null=True, blank=True) # the last time the player eliminated someone
    kills = models.IntegerField('eliminations', default=0, null=True, blank=True)



    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        if not Player.objects.filter(user=instance):
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
        return timezone.now() - self.last_active > timedelta(hours=24)

 
