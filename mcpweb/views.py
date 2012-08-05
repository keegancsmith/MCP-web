import json

from mcp import ClientException
from mcpweb.models import TronGame

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import get_object_or_404


def game(request, game_id):
    game = get_object_or_404(TronGame, id=game_id)
    return HttpResponse('hello %d' % game.id)


def game_api(request, game_id, token):
    game = get_object_or_404(TronGame, id=game_id)

    # The token specifies which player we act as, which will affect the JSON
    # response we return
    if token == game.player1_token:
        player = game.player1
    elif token == game.player2_token:
        player = game.player2
    elif token == 'public':
        player = None
        if request.POST:
            return HttpResponseForbidden('You are not playing in this game')
    else:
        return HttpResponseNotFound()

    if request.POST:
        assert player in game.players
        game_state = request.POST['game_state']
        try:
            game.new_game_state(player, game_state)
            return HttpResponse('success')
        except ClientException as e:
            return HttpResponse(str(e), status=400, content_type='text/plain')

    cache_key = 'trongame-%d-%s' % (game.id, token)
    json_state = cache.get(cache_key, version=game.turn)
    if json_state is None:
        json_state = json.dumps(game.dictify(request, player))
        cache.set(cache_key, json_state, version=game.turn)

    return HttpResponse(json_state, content_type='application/json')
