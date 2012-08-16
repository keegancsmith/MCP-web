import mcp

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


def load_game_state(game_state_str):
    if isinstance(game_state_str, mcp.GameState):
        return game_state_str
    return mcp.GameState.loads(game_state_str)


def generate_game_state():
    return mcp.GameState.random_start_game_state().dumps()


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
    winner = models.CharField(max_length=10, choices=WINNER_CHOICES,
                              default=u'inprogress')
    description = models.CharField(max_length=50,
                                   default='Waiting for player 1 to go.')
    game_state = models.TextField(default=generate_game_state)
    turn = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)
    last_played = models.DateTimeField(default=datetime.now)

    # Tokens can never be 'public', but the length of strings returned by
    # get_random_string are 12, so it shouldn't collide
    player1_token = models.CharField(max_length=10, editable=False,
                                     default=get_random_string)
    player2_token = models.CharField(max_length=10, editable=False,
                                     default=get_random_string)

    class Meta:
        ordering = ['-date_created']

    def get_user(self, num):
        if num is None:
            return None
        return (self.player1, self.player2)[int(num) - 1]

    def get_player_num(self, user):
        if user is None:
            return None
        return self.players.index(user) + 1

    @property
    def current_player(self):
        if self.winner == u'inprogress':
            return self.turn % 2 + 1

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
        if self.player2 == user:
            return gs.flip()
        return gs

    def new_game_state(self, player, new_game_state):
        if player != self.current_user:
            raise Exception('Not %s turn. Currently it is %s turn'
                            % (player, self.current_user))

        # Check if the move is legit
        old_game_state = self.game_state_for_user(player)
        new_game_state = load_game_state(new_game_state)
        old_game_state.validate_move(new_game_state)

        # Move is valid. Update everything (possibly ending the game)
        if self.player1 == player:
            game_state = new_game_state
        else:
            game_state = new_game_state.flip()
        self.game_state = game_state.dumps()
        self.last_played = datetime.now()
        self.turn += 1

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
            self.description = (u'Waiting for player %d to go.'
                                % self.current_player)
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
        self.winner = winner
        self.description = description
        self.last_played = datetime.now()
        self.save()

    def save(self, *args, **kw):
        ret = super(TronGame, self).save(*args, **kw)
        if not self.trongamestatehistory_set.filter(turn=self.turn).exists():
            h = TronGameStateHistory(tron_game=self,
                                     game_state=self.game_state,
                                     turn=self.turn)
            h.save()
        return ret

    def dictify(self, request, player=None):
        url = request.build_absolute_uri(self.get_absolute_url())
        game_state = self.game_state
        if player == self.player2:
            game_state = mcp.GameState.loads(game_state).flip().dumps()

        return {
            'player_num': self.get_player_num(player),
            'current_player': self.current_player,
            'winners': map(self.get_player_num, self.winners),
            'description': self.description,
            'game_state': game_state,
            'url': url,
            'turn': self.turn,
            'players': [dictify_user(self.player1),
                        dictify_user(self.player2)],
        }

    def build_history(self):
        history = [[None] * 30 for _ in range(30)]
        start_player1 = None
        start_player2 = None
        for h in self.trongamestatehistory_set.all():
            gs = load_game_state(h.game_state)
            if h.turn == 0:
                start_player1 = tuple(gs.you)
                start_player2 = tuple(gs.opponent)
                history[gs.you.y][gs.you.x] = 0
                history[gs.opponent.y][gs.opponent.x] = 0
                continue

            p = gs.opponent if h.turn % 2 == 0 else gs.you
            if p.at_pole:
                for x in range(30):
                    history[p.y][x] = h.turn
            else:
                history[p.y][p.x] = h.turn

        return {
            'history': history,
            'turn': self.turn,
            'start_player1': start_player1,
            'start_player2': start_player2,
        }

    @models.permalink
    def get_absolute_url(self):
        return ('tron-game', [str(self.id)])

    def __unicode__(self):
        game_str = u'Tron Game %d' % (self.pk)

        def mark_current_player(p):
            if p == self.current_user:
                return unicode(p) + '*'
            else:
                return unicode(p)
        players_str = u', '.join(map(mark_current_player, self.players))
        if self.winners:
            winners = u' and '.join(map(unicode, self.winners))
            game_str += u' won by %s.' % winners
        return u'%s %s' % (game_str, players_str)


class TronGameStateHistory(models.Model):
    tron_game = models.ForeignKey(TronGame)
    game_state = models.TextField()
    turn = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tron_game', 'turn')
        ordering = ['tron_game', 'turn']

    def __unicode__(self):
        return (u'Tron Game History %d for turn %d'
                % (self.tron_game.id, self.turn))
