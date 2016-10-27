"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import datetime
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    target = ndb.IntegerProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user_name_x = ndb.KeyProperty(required=True, kind='User')
    user_name_y = ndb.KeyProperty(required=True, kind='User')
    whose_turn = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user_name_x, user_name_y, min, max, attempts):
        """Creates and returns a new game"""
        if max < min:
            raise ValueError('Maximum must be greater than minimum')
        game = Game(user_name_x=user_name_x,
                    user_name_y=user_name_y,
                    target=random.choice(range(1, max + 1)),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    whose_turn=user_name_x,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name_x = self.user_name_x.get().name
        form.user_name_y = self.user_name_y.get().name
        form.attempts_remaining = self.attempts_remaining
        form.whose_turn = self.whose_turn.get().name
        form.game_over = self.game_over
        form.message = message
        return form

    # run end game as transactions to ensure all updates occur
    @ndb.transactional(xg=True)
    def end_game(self, won=False):
        """Ends the game - if won is True, the current player won. - if won is
        False, it was a cats game."""
        self.game_over = True
        self.put()
        if (self.whose_turn == self.user_name_x):
            not_turn = self.user_name_y
        else:
            not_turn = self.user_name_x
        cats = not won
        # Add the winners score or cats score
        score = Score(parent=self.whose_turn, opponent=not_turn,
                      date=datetime.today(), won=won, cats=cats,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()
        # Add the losers score or cats score
        score = Score(parent=not_turn, opponent=self.whose_turn,
                      date=datetime.today(), won= False, cats=cats,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    #user = ndb.KeyProperty(required=True, kind='User')
    opponent = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    cats = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.key.parent().get().name,
                         # user_name=self.parent_key().get().name,
                         opponent_name=self.opponent.get().name,
                         won=self.won, cats=self.cats,
                         date=str(self.date), guesses=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name_x = messages.StringField(5, required=True)
    user_name_y = messages.StringField(6, required=True)
    whose_turn = messages.StringField(7, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name_x = messages.StringField(1, required=True)
    user_name_y = messages.StringField(2, required=True)
    min = messages.IntegerField(3, default=1)
    max = messages.IntegerField(4, default=10)
    attempts = messages.IntegerField(5, default=5)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    guess = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    opponent_name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    won = messages.BooleanField(4, required=True)
    cats = messages.BooleanField(5, required=True)
    guesses = messages.IntegerField(6, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
