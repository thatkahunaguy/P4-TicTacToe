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
stalemate is called a cats game.

Many different Guess a Number games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - tictactoe.py: Game playing logic.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional), screen_name (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name_x, user_name_o
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name_x & _y provided must be
    existing users - raises a NotFoundException if not.

    Also adds a task to a task queue to update the average moves remaining
    for active games.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, move, user_name
     **do i need x or y**
    - Returns: GameForm with new game state.
    - Description: Accepts a 'move' which is the coord in the 3x3 game board to
    place the X or O depending on the player and returns the updated state of
    the game.  It must be the player's turn or an Exception is returned.  
    If this causes a game to end, a corresponding Score entity will be created.

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

 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address , & (optional)
    screen_name.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Ancestor is a User entity.

- **Moves**
    - Records all moves made in a game.  Ancestor is a Game entity.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, whose_turn,
    game_over flag, board_state, message, user_name_x, user_name_o).
 - **NewGameForm**
    - Used to create a new game (user_name_x, user_name_o)
 - **MakeMoveForm**
    - Inbound make move form (user_name, game_id, move).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, game_id,
    opponent_id, won_flag, cats_flag, date, moves, x_id).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
