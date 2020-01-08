from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint, choice

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_code = models.IntegerField('secret code', null=True, blank=True, unique=True)
    target = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    alive = models.BooleanField('alive', default=True)
    last_active = models.DateTimeField('last active', null=True, blank=True) # the last time the player eliminated someone
    kills = models.IntegerField('eliminations', default=0)

    def reset(self): # reset codes, 
        players = Player.objects.filter(user__is_staff=False)
        for player in Players:
            player.last_active = timezone.now()
            candidate_code = randint(100, 999)

            while Player.objects.filter(secret_code=candidate_code):
                candidate_code = randint(100, 999)
            player.secret_code = candidate_code

            # select target for player

            while Player.objects.filter(target=candidate_target)
            

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name