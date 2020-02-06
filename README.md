# gotcha
Link to the app: [Online Assassin game manager](https://gotchasite.herokuapp.com/)

## What's Assassin?
Assassin is a game usually played with a large group of people with a very simple premise:

All players are assigned a target (one-to-one) that they need to 'eliminate'

Once a player eliminates their target, they get a new target: the target of their original target

The winner is the last person standing (or whoever has the most eliminations by the end of a given time frame etc.)

### Eliminations?
The method of elimination is of course utterly harmless, and varies from game to game. Usually there is an item designated as the 'murder weapon' (e.g. a rolled up sock) and contacting the target with the item eliminates them. However, there are a couple of catches:

An elimination can't be witnessed by another player who is still alive in the game
There are safe zones where eliminations cannot occur (e.g. stairwells, classrooms, dorm rooms if playing in a campus setting) 

### Speeding up the game to a conclusion
An "open list" system can be implemented to coerce the conclusion of a game. If a player is put on the 'open list', then any player in the game is allowed to eliminate the player. A common way of systematically managing this is by setting a rule where players must eliminate their target (or someone who is on the open list) within a certain time limit (e.g. 24 hours). This also steers away the incentive to just "hide" in safe zones, as this will most likely result you in being put onto the open list.

### Game management
My first exposure to Assassin was in a university-campus setting, and the way in which it was previously managed was purely manual. It involved a game-master/referee to assign and facilitate the exchange of targets. A method of doing this is passing everyone their targets on a small piece of paper (or popstick etc.), so that after a player completes an elimination, they would receive their target's piece of paper, which contains the name of the new target. 

However, the game-master also had to manage the open list; for every single player, keep track of how long it has been since their last completed elimination. With a large number of players (~50), managing the game manually is certain to be tedious and prone to human error (reliant on the players' honesty).

## An automated solution
Converting management from a manual to an automated solution requires three key components:
* A centralised database that keeps track of the players' targets, duration of inactivity, eliminations etc.
* An automated mechanism in which players can report their completed eliminations, given that there is...
* ... a way of ensuring that the players truly did complete their eliminations (as an honesty-based system isn't acceptable anymore)

## A web-based solution
Using a website to manage the game solved all the problems at once;
* Use HTML forms to facilitate the completion and validation of eliminations
* Use Django as a backend to use Python to make the processing of the players' data and its presentation on the web page trivial

### An authentication system
One of the things that you would want with a web-based system is for the players to be able to use the website to view who their targets are. However, without an authentication system, there is no way to distinguish which player is accessing the website. Luckily, Django has a built-in authentication system which makes this very easily implementable.

### Managing multiple games at once
With a relational database model, it’s hard to not consider the idea of running multiple games concurrently; it’s as simple as a single one-to-many relationship. With Django, this is just a matter of creating a new model, say ‘Game’, and adding it to the pre-existing ‘Player’ model as a foreign key. Another consideration is how this fits in with player registration, and the way I handled this by adding an ‘access code’ unique to each game, required upon registration. Of course, an interface also needs to be created for the game-master so they can actually manage the game; to give them the ability to add players onto the open list for misconduct, delete a player if they wish to leave the game etc.

### Basic features:
* Manual elimination/deletion: giving game-masters the ability to manually eliminate someone or delete someone from the game, and allowing players to leave the game on their own accord
* Target reassignments: game-masters can reset the targets mid-game for a fun-twist (or just to be pure evil)
* A ‘graveyard’: a page that has a list of death messages left by players upon elimination
* A personalised rules page: the game-master can write a personal rules page for their game's players (using a django-ckeditor widget)
* A ‘lobby-based’ system: allowing players to register for the game after it has started, and allowing the game-master to add them to the game

#### Extending functionality by implementing background tasks
The key features to be added:
* Scheduling the assignment of targets and the start of the elimination round
* Providing automatic respawns e.g. if a player has been eliminated for 12 hours they respawn

Firstly I experimented with using celery Python library to make these background tasks possible. However, there were many issues that came along with using Celery, starting with the fact that it doesn’t even support Windows anymore, requiring me to switch to Ubuntu for the rest of the project. The final straw came when it was working locally but exhibiting unusual behaviour when in use with a cloud hosted message broker (here is my Stack Overflow post), especially in production.

Finally, django-background-tasks (a database-oriented work queue) came to the rescue, which basically has a long-running process that executes the scheduled tasks (via python manage.py process_tasks). Being far simpler than Celery, and not requiring extra 3rd party addons in deployment made it much more ideal.

### Front-end:
Bootstrap 4.4.
