"""Tic Tac Toe game logic"""
from operator import attrgetter
from google.appengine.api import taskqueue

from models import User, Game, Score, Ranking
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms


def make_move_2(game, player, move):
    if game.game_over:
        return game.to_form('Game already over!')
    # Verify it's the user's turn
    whose_turn = game.whose_turn.get().name
    if not (player == whose_turn):
        return game.to_form(
            "Sorry, it is {}'s turn!".format(whose_turn))
    game.number_of_moves += 1
    index = move.x + 3*move.y
    if game.board[index] == "0":
        # assign the move to the board
        end = game.board[index+1:]
        if index == 9:
            end = ""
        game.board = game.board[:index] + move.kind + end
    else:
        # there is a already a move at this position, don't update game
        return game.to_form("""Sorry, position {}, {} is already filled!"""
                            .format(move.x, move.y))
    # commit the move to the database only after we know its valid
    move.put()
    # only check for game end if at least 5 moves have been made
    if game.number_of_moves > 4:
        if game_over(game, move):
            game.end_game(True)
            game.put()
            return game.to_form('{} wins!'.format(whose_turn))
    #check for cats game chore: make this more robust
    if game.number_of_moves == 9:
        game.cats = True
        game.put()
        return game.to_form('Cats game!')
    # update whose_turn it is
    if game.whose_turn == game.user_name_x:
        game.whose_turn = game.user_name_o
    else:
        game.whose_turn = game.user_name_x
    game.put()
    # notify the other player it is their turn
    taskqueue.add(url='/tasks/turn_notification',
                  params={'user_key': game.whose_turn,
                          'game_key': game.key})
    return game.to_form("It's {}'s turn!".format(game.whose_turn.get().name))


def text_board_to_array(board):
    board_array = [[0, 0, 0] for i in range(3)]
    print "board_array=", board_array
    for i in range(0, 3):
        print "i=", i
        index = 3*i
        print "index=", index
        snippet = board[index:index+3]
        print "snippet=", snippet
        for j in range(0, 3):
            print "j=", j
            char = snippet[j]
            # skip if the space is 0/blank
            if not(char == "0"):
                if char == "X":
                    board_array[i][j] = 1
                else:
                    board_array[i][j] = -1
    return board_array


def game_over(game, move):
    board_array = text_board_to_array(game.board)
    # check row & column of the move & diagonols
    row = col = diag1 = diag2 = 0
    for i in range(0, 3):
        row += board_array[move.y][i]
        col += board_array[i][move.x]
        diag1 += board_array[i][i]
        diag2 += board_array[i][abs(2-i)]
    if abs(row) == 3 or abs(col) == 3 or abs(diag1) == 3 or abs(diag2) == 3:
        return True
    else:
        return False

def rank_them(users, number_of_results):
    rankings = []
    for user in users:
        scores = Score.query(ancestor=user.key)
        wins = losses = cats = moves = 0.0
        for score in scores:
            # chore: might not want to include moves in losses in the
            # rankings algorithm
            moves += score.moves
            if score.won:
                wins += 1.0
            elif score.cats:
                cats += 1.0
            else:
                losses += 1.0
        games = wins + cats + losses
        rating = Ranking(user=user.name,
                         win_percent=wins/games,
                         cats_percent=cats/games,
                         avg_moves=moves/games)
        rankings.append(rating)
    # sorts are stable(order from initial sort retained unless changed
    # by a later sort) so execute the last sort criteria first
    rankings = sorted(rankings, key=attrgetter('avg_moves'))
    rankings = sorted(rankings, key=attrgetter('win_percent',
                                               'cats_percent'),
                                               reverse=True)
    if number_of_results:
        rankings = rankings[:number_of_results]
    return rankings
