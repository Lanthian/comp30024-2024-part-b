"""gamestate.py: Implements a Gamestate data structure that stores game 
information for a current moment in time in a Tetress game."""

__author__ = "Liam Anthian"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

# === Imports ===
from agent.control import make_place
from referee.game import Action, Coord, PlayerColor


class Gamestate:
    """
    Dataclass to represent a state of the game, storing additional information 
    to reduce calculation time.
    """
    # Board represented as a sparse dictionary to save space
    board: dict[Coord, PlayerColor]
    current: PlayerColor
    turn: int  

    # Below count done as to minimise recalculation of dictionary elements
    counts: dict[PlayerColor, int]

    def __init__(self, color: PlayerColor = PlayerColor.RED, turn: int = 1):
        """Constructor method for instantiating and preparing a new Gamestate"""
        self.board = {}
        self.current = color                # Red starts by default
        self.turn = turn                    # First turn is turn 1 by default
        self.counts = {PlayerColor.RED: 0, PlayerColor.BLUE: 0}

    def move(self, action: Action, color: PlayerColor):
        """Apply an Action to a board and update state measures."""
        make_place(self.board, action, color)

        # Not a great implementation, runs in O(k) time.
        self.counts[PlayerColor.RED] = 0
        self.counts[PlayerColor.BLUE] = 0

        for clr in self.board.values():
            self.counts[clr] += 1

        self.current = color.opponent
        self.turn += 1

    def copy(self) -> 'Gamestate':
        """Generates a new Gamestate object with identical stats."""
        new = Gamestate(self.current, self.turn)
        new.board = self.board.copy()
        new.counts = self.counts.copy()
        return new

    def child(self, action: Action, color: PlayerColor) -> 'Gamestate':
        """Generates a new Gamestate object and applys an Action to it, updating
        state measures."""
        new = self.copy()
        new.move(action, color)
        return new


def flatten_board(board: dict[Coord, PlayerColor]) -> str:
    """
    Takes a game board state and converts it into (and returns) a string
    representation, using .__str__() methods of Coord and PlayerColor.
    """
    DELIM = "."

    coord_colors = [(k.__str__() + v.__str__()) for (k,v) in board.items()]
    # Sort to ensure all dictionaries with the same values are equivalent
    coord_colors.sort()
    return DELIM.join(coord_colors)
