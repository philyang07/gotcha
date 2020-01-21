from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from django.utils import timezone
from .models import Game

from celery import shared_task, task

@shared_task
def start_elimination_round(game_pk):
    if not Game.objects.filter(pk=game_pk):
        return # just in case the game doesn't exist anymore!

    game = Game.objects.get(pk=game_pk)

    """
        Scenarios:
            1. move the time forward: ignore older ones, by ensuring that current time (when the task is executed) exceeds the new time
            2. move the time backward: ignore the newer ones, already ensured as the updated task is the first task after the new time (other ones will be in the wrong stage)
    """
    if not game.start_elimination_time:
        return

    if timezone.now() < game.start_elimination_time: # to make sure the right one is executed
        return



    game.start_elimination_time = None
    game.save()
    if len(game.players().filter(secret_code__isnull=False)) < 2 or not game.in_target_sending:
        return

    game.in_progress = True
    game.save()

    for player in game.players().filter(secret_code__isnull=False):
        player.last_active = timezone.now()
        player.save()

@shared_task
def send_targets_and_codes(game_pk):
    if not Game.objects.filter(pk=game_pk):
        return
    
    game = Game.objects.get(pk=game_pk)
    if not game.target_assignment_time:
        return

    # prevent any tasks set 5 minutes past the assignment time to be executed!
    if timezone.now() < game.target_assignment_time:
        return 

    game.target_assignment_time = None # if correct, clear it, if wrong phase, clear it too
    game.save()
    if game.in_registration:
        game.reset()
    
@task()
def test():
    print("pog")


