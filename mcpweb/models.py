import mcp

import random
import string

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


def load_game_state(game_state_str):
    if isinstance(game_state_str, mcp.GameState):
        return game_state_str
    with StringIO(game_state_str) as fd:
        return mcp.GameState.read(fd)


def generate_token():
    valid_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(valid_chars) for _ in xrange(10))


def dictify_user(user):
    return {
        'username': user.username,
    }

class TronGame(models.Model):
    WINNER_CHOICES = (
        (u'inprogress', u'inprogress'),
        (u'player1', u'player1'),
        (u'player2', u'player2'),
        (u'tie', u'tie'),
    )

    DEFAULT_END_GAME_DESCRIPTIONS = {
        u'player1': u'Player 1 wins.',
        u'player2': u'Player 2 wins.',
        u'tie': u'Game ended in a tie.',
    }

    player1 = models.ForeignKey(User, related_name='player1')
    player2 = models.ForeignKey(User, related_name='player2')
    current_player = models.IntegerField(blank=True, null=True, default=1)
    winner = models.CharField(max_length=10, choices=WINNER_CHOICES,
                              default=u'inprogress')
    description = models.CharField(max_length=50)
    game_state = models.TextField()
    turn = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)
    last_played = models.DateTimeField(default=datetime.now)
    player1_token = models.CharField(max_length=10, default=generate_token,
                                     editable=False)
    player2_token = models.CharField(max_length=10, default=generate_token,
                                     editable=False)

    def get_user(self, num):
        if num is None:
            return None
        return (self.player1, self.player2)[int(num) - 1]

    def get_player_num(self, user):
        if user is None:
            return None
        return unicode(self.players.index(user) + 1)

    @property
    def current_user(self):
        return self.get_user(self.current_player)

    @property
    def winners(self):
        if self.winner == u'inprogress':
            return ()
        elif self.winner == u'player1':
            return (self.player1,)
        elif self.winner == u'player2':
            return (self.player2,)
        else:
            assert self.winner == u'tie'
            return (self.player1, self.player2)

    @property
    def players(self):
        return (self.player1, self.player2)

    def game_state_for_user(self, user=None):
        gs = load_game_state(self.game_state)
        if self.get_player_num(user) == '2':
            return gs.flip()
        return gs

    def new_game_state(self, user, new_game_state):
        assert user == self.current_user

        # Check if the move is legit
        old_game_state = self.game_state_for_user(user)
        new_game_state = load_game_state(new_game_state)
        old_game_state.validate_move(new_game_state)

        # Move is valid. Update everything (possibly ending the game)
        if self.player1 == user:
            game_state = new_game_state
        else:
            game_state = new_game_state.flip()
        with StringIO() as fd:
            game_state.write(fd)
            self.game_state = fd.getvalue()

        self.last_played = datetime.now()

        can_move = lambda p: len(list(game_state.neighbours(p))) > 0
        p1_can_move = can_move(game_state.you)
        p2_can_move = can_move(game_state.opponent)
        if not p1_can_move and not p2_can_move:
            self.end_game('tie')
        elif not p1_can_move:
            self.end_game('player2')
        elif not p2_can_move:
            self.end_game('player1')
        else:
            self.current_player = self.get_player_num(user) % 2 + 1
            self.description = (u'Waiting for player %d to go.'
                                % self.current_player)
            self.turn += 1
            self.save()

    def end_game(self, winner, description=None):
        if isinstance(winner, (tuple, list)):
            if len(winner) == 2:
                winner = u'tie'
            else:
                assert len(winner) == 1
                winner = u'player%d' % self.get_player_num(winner[0])
        if description is None:
            description = TronGame.DEFAULT_END_GAME_DESCRIPTIONS[winner]
        self.current_player = None
        self.winner = winner
        self.description = description
        self.last_played = datetime.now()
        self.save()

    def dictify(self, user=None):
        uni = lambda s: None if s is None else unicode(s)

        return {
            'player_num': self.get_player_num(user),
            'current_player': uni(self.current_player),
            'winners': map(self.get_player_num, self.winners),
            'description': self.description,
            'game_state': self.game_state,
            'url': self.get_absolute_url(),
            'players': [],
        }

    @models.permalink
    def get_absolute_url(self):
        return ('tron-game', [str(self.id)])

    def __unicode__(self):
        game_str = u'Tron Game %d - %s' % (self.pk, self.name)

        def mark_current_player(p):
            if p == self.current_user:
                return unicode(p) + '*'
            else:
                return unicode(p)
        players_str = u', '.join(map(mark_current_player, self.players))
        if self.winners:
            game_str += u' won by %s' % unicode(self.winners)
        return u'%s %s' % (game_str, players_str)


class TronGameStateHistory(models.Model):
    tron_game = models.ForeignKey(TronGame)
    game_state = models.TextField()
    turn = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tron_game', 'turn')
