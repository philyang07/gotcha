from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint, choice
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_code = models.IntegerField('secret code', null=True, blank=True, unique=True)
    target = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    alive = models.BooleanField('alive', default=True)
    last_active = models.DateTimeField('last active', null=True, blank=True) # the last time the player eliminated someone
    kills = models.IntegerField('eliminations', default=0)

    def reset(): # reset codes, 
        players = Player.objects.filter(user__is_staff=False)

        # clear everything
        for player in players:
            player.alive = True
            player.secret_code = None
            player.target = None
            player.save()

        for player in players:
            player.last_active = timezone.now()
            candidate_code = randint(100, 999)

            while Player.objects.filter(secret_code=candidate_code):
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

        first_target = last_target = choice(players)
        last_killer = choice(Player.objects.filter(target=None).exclude(pk=first_target.pk))
        while Player.objects.filter(target=None).exclude(pk=first_target.pk):
            last_killer.target = last_target
            last_killer.save()
            last_target = last_killer
            if Player.objects.filter(target=None).exclude(pk=first_target.pk):
                last_killer = choice(Player.objects.filter(target=None).exclude(pk=first_target.pk))
        first_target.target = last_killer
        first_target.save()

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        player = Player(user=instance)
        player.save()
        instance.player = player