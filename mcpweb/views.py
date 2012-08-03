import json

from mcp import ClientException
from mcpweb.models import TronGame

from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import get_object_or_404


def game(request, game_id, token=None):
    game = get_object_or_404(TronGame, id=game_id)

    # If the token matches one of the player tokens, we act as that User
    if token is not None:
        token = token.strip('/')
        if token == game.player1_token:
            user = game.player1
        elif token == game.player2_token:
            user = game.player2
        else:
            return HttpResponseNotFound()
    elif request.user.is_authenticated():
        user = request.user
    else:
        user = None

    if request.POST:
        return game_post(request, game, user)

    return HttpResponse(json.dumps(game.dictify(request, user)),
                        content_type='application/json')


def game_post(request, game, user):
    if user not in game.players:
        return HttpResponseForbidden('You are not playing in this game')
    game_state = request.POST['game_state']
    try:
        game.new_game_state(user, game_state)
        return HttpResponse('success')
    except ClientException as e:
        return HttpResponse(str(e), status=400, content_type='text/plain')
