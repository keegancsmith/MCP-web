==============
 Game Payload
==============

When requesting the state of a game from the server a JSON associative array
is returned describing the state of the current game. The schema of the array
is::

  {
    'player_num': ['1' | '2' | null],
    'turn': ['1' | '2' | null],
    'winner': ['1' | '2' | 'tie' | null],
    'description': '', // Description of the current state of the game
    'game_state': '', // The gamestate file as described in the specification
    'url': '', // Public URL for the game
    'players': [
      { ... }, // Player 1
      { ... }  // Player 2
    ]
  }

To play a turn just POST the game_state to your Game URL.
