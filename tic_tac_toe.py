"""Tic Tac Toe game logic"""
from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms


def make_move_2(game, player, guess):
    if game.game_over:
        return game.to_form('Game already over!')
    # Verify it's the user's turn
    whose_turn = game.whose_turn.get().name
    if not (player == whose_turn):
        return game.to_form(
            "Sorry, it is {}'s turn!".format(whose_turn))
    game.attempts_remaining -= 1
    if guess == game.target:
        game.end_game(True)
        return game.to_form('You win!')

    if guess < game.target:
        msg = 'Too low!'
    else:
        msg = 'Too high!'

    if game.attempts_remaining < 1:
        game.end_game(False)
        return game.to_form(msg + ' Game over!')
    else:
        # update whose_turn it is
        if game.whose_turn == game.user_name_x:
            game.whose_turn = game.user_name_y
        else:
            game.whose_turn = game.user_name_x
        game.put()
        return game.to_form(msg)
