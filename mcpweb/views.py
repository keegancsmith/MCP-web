import json

from mcp import ClientException
from mcpweb.models import TronGame

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import get_object_or_404


def game(request, game_id, token=None):
    game = get_object_or_404(TronGame, id=game_id)

    # If the token matches one of the player tokens, we act as that User
    player = None
    if token is not None:
        token = token.strip('/')
        if token == game.player1_token:
            player = game.player1
        elif token == game.player2_token:
            player = game.player2
        else:
            return HttpResponseNotFound()
    elif request.user in game.players:
        player = request.user

    if request.POST:
        return game_post(request, game, player)

    cache_suffix = 'public' if player is None else player.id
    cache_key = 'trongame-%d-%s' % (game.id, cache_suffix)
    json_state = cache.get(cache_key, version=game.turn)
    if json_state is None:
        json_state = json.dumps(game.dictify(request, player))
        cache.set(cache_key, json_state, version=game.turn)

    return HttpResponse(json_state, content_type='application/json')


def game_post(request, game, player):
    if player is None:
        return HttpResponseForbidden('You are not playing in this game')
    else:
        assert player in game.players

    game_state = request.POST['game_state']
    try:
        game.new_game_state(player, game_state)
        return HttpResponse('success')
    except ClientException as e:
        return HttpResponse(str(e), status=400, content_type='text/plain')
