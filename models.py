"""models.py - This file contains the class definitions for the Datastore
entities and regular objects used by the Tic Tac Toe. Helper methods like
'to_form', 'new_game', & 'end_game' are used to support RPC messaging and
Datastore operations on the entities"""

from datetime import datetime
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Move(ndb.Model):
    """Move object"""
    kind = ndb.StringProperty(required=True, default="X", choices=["X", "O"])
    # chore: add a validator to x & y to ensure they are between 0 & 2
    # validated input in the endpoint, could still add here
    x = ndb.IntegerProperty(required=True)
    y = ndb.IntegerProperty(required=True)
    number = ndb.IntegerProperty(required=True)
    board = ndb.StringProperty()
    status = ndb.StringProperty()

    def to_form(self):
        return MoveForm(kind=self.kind, x=self.x, y=self.y,
                        number=self.number, board=self.board,
                        status=self.status)


class Game(ndb.Model):
    """Game object"""
    number_of_moves = ndb.IntegerProperty(required=True, default=0)
    board = ndb.StringProperty(required=True, default="000000000")
    game_over = ndb.BooleanProperty(required=True, default=False)
    user_name_x = ndb.KeyProperty(required=True, kind='User')
    user_name_o = ndb.KeyProperty(required=True, kind='User')
    whose_turn = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user_name_x, user_name_o):
        """Creates and returns a new game"""
        game = Game(user_name_x=user_name_x,
                    user_name_o=user_name_o,
                    number_of_moves=0,
                    whose_turn=user_name_x,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name_x = self.user_name_x.get().name
        form.user_name_o = self.user_name_o.get().name
        form.whose_turn = self.whose_turn.get().name
        form.game_over = self.game_over
        form.message = message
        form.board = self.board
        form.number_of_moves = self.number_of_moves
        return form

    # run end game as transactions to ensure all updates occur
    @ndb.transactional(xg=True)
    def end_game(self, won=False):
        """Ends the game - if won is True, the current player won. - if won is
        False, it was a cats game."""
        self.game_over = True
        if (self.whose_turn == self.user_name_x):
            not_turn = self.user_name_o
        else:
            not_turn = self.user_name_x
        cats = not won
        self.cats = cats
        self.put()
        # Add the winners score or cats score
        score = Score(parent=self.whose_turn, opponent=not_turn,
                      date=datetime.today(), won=won, cats=cats,
                      moves=self.number_of_moves)
        score.put()
        # Add the losers score or cats score
        score = Score(parent=not_turn, opponent=self.whose_turn,
                      date=datetime.today(), won=False, cats=cats,
                      moves=self.number_of_moves)
        score.put()


class Score(ndb.Model):
    """Score object"""
    opponent = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    cats = ndb.BooleanProperty(required=True)
    moves = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.key.parent().get().name,
                         opponent_name=self.opponent.get().name,
                         won=self.won, cats=self.cats,
                         date=str(self.date), moves=self.moves)


class Ranking(object):
    """Ranking object"""
    def __init__(self, user, win_percent, cats_percent, avg_moves):
        self.user = user
        self.win_percent = win_percent
        self.cats_percent = cats_percent
        self.avg_moves = avg_moves

    def to_form(self):
        return RankingForm(user=self.user, win_percent=self.win_percent,
                           cats_percent=self.cats_percent,
                           avg_moves=self.avg_moves)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    number_of_moves = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name_x = messages.StringField(5, required=True)
    user_name_o = messages.StringField(6, required=True)
    whose_turn = messages.StringField(7, required=True)
    board = messages.StringField(8, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name_x = messages.StringField(1, required=True)
    user_name_o = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move_x = messages.IntegerField(2, required=True)
    move_y = messages.IntegerField(3, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    opponent_name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    won = messages.BooleanField(4, required=True)
    cats = messages.BooleanField(5, required=True)
    # number of moves
    moves = messages.IntegerField(6, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class MoveForm(messages.Message):
    """MoveForm for outbound Move information"""
    # x or y
    kind = messages.StringField(1, required=True)
    x = messages.IntegerField(2, required=True)
    y = messages.IntegerField(3, required=True)
    number = messages.IntegerField(4, required=True)
    board = messages.StringField(5, required=True)
    status = messages.StringField(6, required=True)


class MoveForms(messages.Message):
    """Return multiple MoveForms"""
    items = messages.MessageField(MoveForm, 1, repeated=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class RankingRequestForm(messages.Message):
    """RankingForm for inbound ranking request"""
    number_of_results = messages.IntegerField(1)


class RankingForm(messages.Message):
    """RankingForm for outbound ranking information"""
    user = messages.StringField(1, required=True)
    win_percent = messages.FloatField(2, required=True)
    cats_percent = messages.FloatField(3, required=True)
    avg_moves = messages.FloatField(4, required=True)


class RankingForms(messages.Message):
    """Return multiple RankingForms"""
    items = messages.MessageField(RankingForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
