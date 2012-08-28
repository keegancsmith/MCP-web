import mcp

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
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


class TronGameHistory(object):
    def __init__(self, state=None):
        if state is None:
            state = {}
        self.state = state
        self._p1_turn = None
        self._p2_turn = None

    @property
    def p1_turn(self):
        if self._p1_turn is None:
            if self.state:
                self._p1_turn = max(self.state.itervalues()) + 1
            else:
                self._p1_turn = 1
        return self._p1_turn

    @property
    def p2_turn(self):
        if self._p2_turn is None:
            if self.state:
                self._p2_turn = -(min(self.state.itervalues()) - 1)
            else:
                self._p2_turn = 1
        return self._p2_turn

    def add_move(self, is_player1, pos):
        if is_player1:
            self.state[pos] = self.p1_turn
            self._p1_turn += 1
        else:
            self.state[pos] = -self.p2_turn
            self._p2_turn += 1

    @classmethod
    def loads(cls, s):
        state = {}
        for line in s.splitlines():
            x, y, turn = map(int, line.split())
            state[mcp.Position(x, y)] = turn
        return cls(state)

    def dumps(self):
        return '\n'.join('%d %d %d' % (p.x, p.y, t)
                         for p, t in self.state.iteritems())

    def dump_rows(self):
        rows = [[0] * 30 for _ in range(30)]
        for p, turn in self.state.iteritems():
            if p.at_pole:
                for x in range(30):
                    rows[p.y][x] = turn
            else:
                rows[p.y][p.x] = turn
        return rows

    def assert_consistent(self, game_state):
        count_p1 = 0
        count_p2 = 0
        for p, v in game_state:
            if v == 'Clear':
                assert p not in self.state
            elif 'You' in v:
                count_p1 += 1
                assert self.state[p] > 0
            else:
                count_p2 += 1
                assert self.state[p] < 0
        assert self.state[game_state.you] == self.p1_turn - 1
        assert -self.state[game_state.opponent] == self.p2_turn - 1
        assert count_p1 == self.p1_turn - 1
        assert count_p2 == self.p2_turn - 1
        assert len(set(self.state.itervalues())) == len(self.state)


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
    game_history = models.TextField(default='')
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

        # game history
        is_player1 = self.turn % 2 == 1
        pos = game_state.you if is_player1 else game_state.opponent
        assert is_player1 == (self.player1 == player)
        gh = self.game_history
        if not isinstance(gh, TronGameHistory):
            gh = TronGameHistory.loads(gh)
        gh.add_move(is_player1, pos)
        self.game_history = gh

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
        gs = load_game_state(self.game_state)
        if self.turn == 0:
            # On the initial state we need to setup the game history
            gh = TronGameHistory({gs.you: 1, gs.opponent: -1})
        else:
            gh = self.game_history
        if not isinstance(gh, TronGameHistory):
            gh = TronGameHistory.loads(gh)
        gh.assert_consistent(gs)
        self.game_state = gs.dumps()
        self.game_history = gh.dumps()
        return super(TronGame, self).save(*args, **kw)

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
        gh = self.game_history
        if not isinstance(gh, TronGameHistory):
            gh = TronGameHistory.loads(gh)

        return {
            'history': gh.dump_rows(),
            'p1_moves': gh.p1_turn - 1,
            'p2_moves': gh.p2_turn - 1,
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


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    auth_token = models.CharField(max_length=10, default=get_random_string)

    def __unicode__(self):
        return unicode(self.user)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
