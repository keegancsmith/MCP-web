import json

from mcp import ClientException
from mcpweb.models import TronGame
from mcpweb.forms import AuthenticationForm, NewTronGameForm, UserCreationForm

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import condition


def game_view(func):
    def f(request, game_id, *args, **kw):
        game = get_object_or_404(TronGame, pk=game_id)
        request.game = game
        return func(request, *args, **kw)
    return f


@game_view
def game_viewer(request):
    game = request.game
    user = request.user

    context = {
        'game': game,
        'title': (u'Game %d - %s vs %s'
                  % (game.id, game.player1.username, game.player2.username)),
    }
    game_url = request.build_absolute_uri(game.get_absolute_url())
    if user.is_superuser or user == game.player1:
        context['player1_url'] = '%s%s/' % (game_url, game.player1_token)
    if user.is_superuser or user == game.player2:
        context['player2_url'] = '%s%s/' % (game_url, game.player2_token)

    return render(request, 'mcpweb/game_viewer.html', context)


@game_view
@condition(etag_func=lambda r, *a, **k: str(r.game.turn),
           last_modified_func=lambda r, *a, **k: r.game.last_played)
def game_api(request, token):
    game = request.game

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


@csrf_protect
@login_required
def new_game(request):
    if request.method == 'POST':
        form = NewTronGameForm(request.POST)
        if form.is_valid():
            game = form.create_game(request.user)
            return HttpResponseRedirect(game.get_absolute_url())
    else:
        form = NewTronGameForm()

    return render(request, 'mcpweb/form.html',
                  {'form': form, 'title': 'New Game'})


@csrf_protect
def home(request):
    context = {
        'signup_form': UserCreationForm(),
        'login_form': AuthenticationForm(request),
    }

    if request.user.is_authenticated():
        context['active'] = TronGame.objects.filter(winner=u'inprogress')
        context['finished'] = TronGame.objects.exclude(winner=u'inprogress')

    return render(request, 'mcpweb/home.html', context)


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tron-home'))
    else:
        form = UserCreationForm()

    return render(request, 'mcpweb/form.html',
                  {'form': form, 'title': 'Login'})


@csrf_protect
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return HttpResponseRedirect(reverse('tron-home'))
    else:
        form = AuthenticationForm(request)

    return render(request, 'mcpweb/form.html',
                  {'form': form, 'title': 'Login'})
