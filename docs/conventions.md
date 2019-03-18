# Conventions

##### Querying in Controllers:

Good:

    @login_required
    def update_snake(request, id):
        snake = request.user.profile.snakes.get(id=id)
        ...

Avoid:

    @login_required
    def update_snake(request, id):
        snake = Snake.objects.get(id=id)
        ...

This leads to subtle cross profile / account access issues. It's much easier to always start with a 'base query' context that ensures that every query after that will fetch information for the current user.

In general a good rule is: If you see capital model letters this means the endpoint is probably public.

##### Url patterns:

- Always use `django.urls.path` instead of the deprecated `django.conf.urls.url`.
- Always use trailing slashes in urls.

##### Url Naming:

A typical restful setup for a set of resources:

    GET  /games/          name=games     - views.games.index
    GET  /games/new/      name=new_game  - views.games.new
    POST /games/new/      name=new_game  - views.games.create
    GET  /games/:id/      name=game      - views.games.show
    GET  /games/:id/edit/ name=edit_game - views.games.edit
    PUT  /games/:id/edit/ name=edit_game - views.games.update

A typical restful setup for a single resource:

    GET  /game/      name=game      - views.games.show
    GET  /game/new/  name=new_game  - views.games.new
    POST /game/new/  name=new_game  - views.games.create
    GET  /game/edit/ name=edit_game - views.games.edit
    PUT  /game/edit/ name=edit_game - views.games.update

##### App Structures

Dependency graph of imports should look like this! If you have an import that doesn't fit in a model like this we should talk about it.

    authentication -> core -> tournament
                           -> leaderboard
                           -> arena
                           -> learn

###### Core

Holds all core models.

Models:
- Profile - (Represents a user that actively plays in the app)
- Team'   - (Represents a team of players)
- Badge'  - (Given by the bounties module)
- Snake   - (Points to either a player or a team)
- Game

Urls:
- / <- list of all games
- /u/
- /s/
- /g/

**Note: To attach snakes, games and other objects to users attach them to the
Profile object. This keeps our PII and authentication modules separate.**

###### Authentication

Models:
- User

###### Learn

Holds the learn app.

Urls:
- /learn/

###### Arena

Models:
- Arena - (Continually runs matches)

Urls:
- /arenas/

###### Tournament

Models:
- Tournament
- Bracket
- Heat - (Attaches snakes to given heats)

Urls:
- /tournament/
