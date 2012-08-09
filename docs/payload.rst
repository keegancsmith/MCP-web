==============
 Game Payload
==============

When requesting the state of a game from the server a JSON associative array
is returned describing the state of the current game. The schema of the array
is::

  {
    'player_num': [1 | 2 | null],
    'current_player': [1 | 2 | null],
    'winners': [], // List of winner numbers
    'description': '', // Description of the current state of the game
    'game_state': '', // The gamestate file as described in the specification
    'url': '', // Public URL for the game
    'turn': 0, // The turn number. Initially zero. Increments for each turn played
    'players': [
      { ... }, // Player 1
      { ... }  // Player 2
    ]
  }

To play a turn just POST the game_state to your Game URL.

Winners is an empty list if the game is in progress. Otherwise it contains the
winning player numbers. Note there can be two in the case of a tie.
