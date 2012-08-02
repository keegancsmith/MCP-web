import json

from mcpweb.models import TronGame

from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def game(request, game_id, token=None):
    game = get_object_or_404(TronGame, id=game_id)

    # If the token matches one of the player tokens, we act as that User
    if token is not None:
        token = token.strip('/')
    elif request.user.is_authenticated():
        user = request.user
    else:
        user = None

    if request.POST:
        return game_post(request, game, user)

    return HttpResponse(json.dumps(game.dictify(request, user)),
                        content_type='application/json')


def game_post(request, game, user):
    # TODO
    pass
