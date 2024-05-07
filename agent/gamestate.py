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

    def __init__(self):
        """Constructor method for instantiating and preparing a new Gamestate"""
        self.board = {}
        self.current = PlayerColor.RED                  # Red starts
        self.turn = 1                                   # First turn is turn 1
        self.counts = {PlayerColor.RED: 0, PlayerColor.BLUE: 0}

    def move(self, action: Action, color: PlayerColor):
        make_place(self.board, action, color)

        # todo - not a good implementation atm, just temporary
        self.counts[PlayerColor.RED] = 0
        self.counts[PlayerColor.BLUE] = 0

        for clr in self.board.values():
            self.counts[clr] += 1

        self.current = color.opponent
        self.turn += 1

    def copy(self) -> 'Gamestate':
        new = Gamestate()
        new.board = self.board.copy()
        new.current = self.current
        new.counts = self.counts.copy()
        return new

    def child(self, action: Action, color: PlayerColor) -> 'Gamestate':
        new = self.copy()
        new.move(action, color)
        return new
