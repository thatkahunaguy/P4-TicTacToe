#Full Stack Nanodegree Project 4
#Tic Tac Toe Game API

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.


##Game Description:
Tic Tac Toe is a simple game. The object of Tic Tac Toe is to get 3 in a
row. You play on a 3 by 3 game board. The first player is known as X
and the second is O. Players alternate placing Xs and Os on the game board
until either opponent has 3 in a row or all nine squares are filled. X
always goes first, and in the event that no one has three in a row, the
stalemate is called a cats game.  To make a move, provide the x,y coordinate
in the 3x3 grid for the player to make a move.  For example, the top left
corner is 0,0 (move_x=0, move_y=0) and the bottom right corner is 2,2.

##Scoring & Ranking:
Since this is a 2 player game, "high scores" were not implemented per the
assignment rubric.  When each game concludes, the player's result (Win? Cats?)
is recorded along with the number of moves in the game.  For purposes of
rankings, a player's win percentage is used to rank followed by the cats
game percentage as a tiebreaker and then average number of moves as the final
tiebreaker(fewer is better).

##Files Included:
 - api.py: Contains endpoints.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue tasks.
 - models.py: Entity and message definitions including helper methods.
 - tictactoe.py: Game playing logic.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name_x, user_name_o
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name_x & _y provided must be
    existing users - raises a NotFoundException if not. These are the X &
    Y players in the game.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, move_x, move_y
    - Returns: GameForm with new game state.
    - Description: Accepts a 'move' which is the coord in the 3x3 game board to
    place the X or O depending on the player and returns the updated state of
    the game.  It must be the player's turn or an Exception is returned.  
    If this causes a game to end, a corresponding Score entity will be created.
    Creates a taskqueue to notify the other player by email it is their turn
    as long as the player provided an email.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**
   - Path: 'games/user/{user_name}'
   - Method: GET
   - Parameters: user_name, email
   - Returns: GameForms.
   - Description: Returns all Games played by the provided player (unordered).
   Will raise a NotFoundException if the User does not exist.

- **get_moves**
   - Path: 'game/moves/{urlsafe_game_key}'
   - Method: GET
   - Parameters: urlsafe_game_key
   - Returns: MoveForms.
   - Description: Returns all moves in the game in the order played.

 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

- **get_user_rankings**
   - Path: 'rankings
   - Method: GET
   - Parameters: number_of_results(optional)
   - Returns: StringMessage
   - Description: Returns the list of user rankings from 1st place to
   number_of_results (or all if not provided).  Rankings are win/loss ratio
   with ties broken by cats game ratio with further ties broken by average
   number of moves.  Users who have not played a game are not ranked.

- **cancel_game**
  - Path: 'game/cancel/{urlsafe_game_key}'
  - Method: PUT
  - Parameters: urlsafe_game_key
  - Returns: GameForm.
  - Description: Cancels the specified game and returns the final game state.

##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address , & (optional)
    screen_name.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Ancestor is a User entity.

- **Move**
    - Stores all moves made in a game.  Ancestor is a Game entity.

- **Ranking**
    - An object user to store win, loss, & cats percentages for ranking.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, whose_turn,
    game_over flag, board_state, message, user_name_x, user_name_o).
 - **NewGameForm**
    - Used to create a new game (user_name_x, user_name_o)
 - **MakeMoveForm**
    - Inbound make move form (user_name, move_x, move_y).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name,
    opponent_name, won_flag, cats_flag, date, moves).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **MoveForm**
    - Representation of a completed move (kind - ie X or Y,
    x, y, number - ie move 1, 2 etc).
 - **MoveForms**
    - Multiple MoveForm container.
 - **GameForms**
    - Multiple GameForm container.
 - **RankingRequestForm**
    - Used to request user rankings (number_of_results - optionally limits
    the returned results to this number)
 - **RankingForm**
    - Represents ranking information for a single user (user, win_percent,
    cats_percent, avg_moves)
 - **RankingForms**
    - Multiple RankingForm container.
 - **StringMessage**
    - General purpose String container.
