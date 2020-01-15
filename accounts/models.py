from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from random import randint, choice
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from datetime import timedelta
from ckeditor.fields import RichTextField
import string

# Create your models here.
class GamePlayerManager(models.Manager):
    use_for_related_fields = True
    def query_set(self):
        return super().get_queryset().filter()


class Game(models.Model):
    access_code = models.CharField('access code', max_length=5, unique=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    in_progress = models.BooleanField('in progess', default=False)
    rules = RichTextField(blank=True, null=True, default=None)
    # rules = models.TextField('rules', max_length=1000, default=None)


    class Meta:
        permissions = [
            ("game_admin", "Can view game statistics"),
        ]

    def players(self):
        return self.player_set.filter(game=self).exclude(Q(user__user_permissions__codename="accounts.game_admin"))

    @property
    def has_sent_info(self):
        """
            Defined as being the stage when at least one player has a secret code
        """
        return self.players().filter(secret_code__isnull=False)
        
    @property
    def winner(self):
        alive_players = self.players().filter(alive=True, secret_code__isnull=False)
        if self.in_progress and len(alive_players) == 1:
            return alive_players[0]
        return None

    def generate_access_code():
        existing_access_codes = [g.access_code for g in Game.objects.all()]
        candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        while candidate_code in existing_access_codes:
            candidate_code = "".join([choice(string.ascii_uppercase) for i in range(4)])
        return candidate_code

    def __str__(self):
        return self.access_code + " - " + self.admin.email

    def populate_players(self):
        for i in range(5):
            email = Game.generate_access_code().lower() + "@gmail.com"
            first_name = Game.generate_access_code().lower().capitalize()
            last_name = Game.generate_access_code().lower().capitalize()

            user = User.objects.create_user(email, email, 123, 
                                    first_name=first_name,
                                    last_name=last_name)
            user.save()
            user.player.game = self
            user.player.alive = True
            user.player.save()

    def initialize_players(self, in_game=False, with_code=False):
        players = self.players()
        if in_game:
            players = players.filter(secret_code__isnull=False)

        for player in players:
            player.initialize(with_code=with_code)


    def reset(self, to_start=False): # resets the players after registration stage
        if to_start:
            # the self.in_progress shouldn't matter; as the players not in the game don't have codes anyway
            self.initialize_players(in_game=self.in_progress, with_code=False)
            self.in_progress = False
            self.save()
        else:
            self.initialize_players(in_game=self.in_progress, with_code=True)
            self.reassign_targets()

    def delete_game(self):
        player_pks = [p.pk for p in self.players()]
        for pk in player_pks:
            Player.objects.get(pk=pk).manual_delete()
        self.admin.delete()

    def reassign_targets(self):
        players = self.players().filter(alive=True, secret_code__isnull=False)

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
    death_message = models.TextField('death message', max_length=300, default="Was eliminated.")

    class Meta:
        unique_together = ('game', 'secret_code',)


    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return self.user.first_name + " " + self.user.last_name
        return "player " + str(self.pk) + " " + self.user.email

    def initialize(self, with_code=False, keep_kills=False):
        if not keep_kills:
            self.kills = 0
        self.manual_open = False
        self.alive = True
        self.secret_code = None
        self.last_active = None

        if self.game.in_progress and not self.game.winner:
            self.last_active = timezone.now()
        
        if with_code:
            candidate_code = randint(100, 999)

            players = self.game.players()
            while players.filter(secret_code=candidate_code):
                candidate_code = randint(100, 999)
            self.secret_code = candidate_code

        self.save()

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        if not Player.objects.filter(user=instance) and not instance.has_perm("accounts.game_admin"):
            player = Player(user=instance)
            player.save()
            instance.player = player

    @property
    def inactivity_duration(self):
        if not self.last_active: # game hasn't started, or if it has, they are a 'new player'
            return None
    

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
            return False
        return self.alive and (self.manual_open or timezone.now() - self.last_active > timedelta(hours=24))

    def manual_delete(self):
        player = self
        player_user = player.user
        if Player.objects.filter(target=player):
            player_killer = Player.objects.get(target=player)
            if player.target == player_killer: # scenario when two players are left, and one leaves
                player_killer.target = None
            else:
                player_killer.target = player.target
            player.target = None
            player.save()
            player_killer.save()
            player.delete()
        player_user.delete()     

    def manual_kill(self):
        if self.game.winner == self: # not necessary to have the == self but shouldn't matter
            return True

        player = self

        if Player.objects.filter(target=player) and player.last_active: # equivalent them to being alive
            player_killer = Player.objects.get(target=player)
            if player.target == player_killer: # when only two players are left
                player_killer.target = None
            else: 
                player_killer.target = player.target
            player.target = None
            player.last_active = timezone.now()
            player.alive = False
            player.manual_open = False
            player.save()
            player_killer.save()   
        else:
            return True

    def manual_add(self):
        game = self.game
        """
            If they are not in the game:
                1. Choose a random person in the game (alive)
                2. This person will be the killer of this guy
                3. This guy, will now kill the target of the random person
        """

        alive_players = game.players().filter(alive=True, secret_code__isnull=False)
        
        if len(alive_players) == 1:
            only_player = alive_players[0]
            only_player.target = self
            self.target = only_player
            only_player.save()
        elif len(alive_players) > 1:
            random_alive = choice(alive_players)
            random_alive_target = random_alive.target
            random_alive.target = self
            random_alive.save()
            self.target = random_alive_target
        
        if self.secret_code: # 
            self.initialize(with_code=True, keep_kills=True)
        else:
            self.initialize(with_code=True)

