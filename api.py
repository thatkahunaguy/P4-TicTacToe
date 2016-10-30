# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import User, Game, Score, Move
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, MoveForm, MoveForms
from utils import get_by_urlsafe
from tic_tac_toe import make_move_2

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
CANCEL_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    urlsafe_game_key=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='tictactoe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user_x = User.query(User.name == request.user_name_x).get()
        user_o = User.query(User.name == request.user_name_o).get()
        if not user_x or not user_o:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user_x.key, user_o.key, request.min,
                                 request.max, request.attempts)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.whose_turn == game.user_name_x:
            kind = "X"
        else:
            kind = "O"
        move = Move(parent=game.key, kind=kind,
                    number=game.number_of_moves + 1,
                    x=request.move_x, y=request.move_y)
        return make_move_2(game=game, player=request.user_name,
                           move=move)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=MoveForms,
                      path='game/moves/{urlsafe_game_key}',
                      name='get_moves',
                      http_method='GET')
    def get_moves(self, request):
        """Gets all moves for a particular game"""
        game_key = ndb.Key(urlsafe=request.urlsafe_game_key)
        moves = Move.query(ancestor=game_key).order(Move.number)
        return MoveForms(items=[move.to_form() for move in moves])

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        # scores = Score.query(Score.user == user.key)
        scores = Score.query(ancestor=user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        user = user.key
        # chore: figure out why I don't have to call fetch on they
        # queries for games and scores above - thought this just
        # built a query object and didn't actually query the database
        # without .fetch() or .get() - see the link below...when used
        # as an iterator the query instance returns results when it is
        # iterated over
        # http://stackoverflow.com/questions/15410609/google-app-engine-ndb-need-to-fetch-after-query
        games = Game.query(Game.game_over == False,
                           ndb.OR(Game.user_name_x == user,
                                  Game.user_name_o == user))
        return GameForms(items=[game.to_form("active game") for game in games])

    @endpoints.method(request_message=CANCEL_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels a game if not finished and user is a game member"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if user.key == game.user_name_x or user.key == game.user_name_o:
            if not game.game_over:
                game.key.delete()
                return game.to_form("Game cancelled!")
            else:
                return game.to_form("Sorry, this game is fnished!")
        else:
            return game.to_form(
                "Sorry, {} can't cancel this game".format(user.name))


    # @endpoints.method(response_message=StringMessage,
    #                   path='games/average_attempts',
    #                   name='get_average_attempts_remaining',
    #                   http_method='GET')
    # def get_average_attempts(self, request):
    #     """Get the cached average moves remaining"""
    #     return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')
    #
    # @staticmethod
    # def _cache_average_attempts():
    #     """Populates memcache with the average moves remaining of Games"""
    #     games = Game.query(Game.game_over == False).fetch()
    #     if games:
    #         count = len(games)
    #         total_attempts_remaining = sum([game.attempts_remaining
    #                                     for game in games])
    #         average = float(total_attempts_remaining)/count
            # memcache.set(MEMCACHE_MOVES_REMAINING,
            #              'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([TicTacToeApi])
