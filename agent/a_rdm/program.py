"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module. 
Agent selects next move at random."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from random import choice

from agent.control import first_move, possible_moves
from agent.gamestate import Gamestate
from referee.game import Action, PlayerColor


class Agent:
    """
    This class is the "entry point" for an agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool
    color: PlayerColor
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        All setup and/or precomputation is done here.
        """
        self.first_move=True
        self.color = color
        self.game = Gamestate()

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. Always returns an action object. 
        """
        # Select first move based on first_move() function
        if self.first_move:
            self.first_move=False
            return first_move(self.game.board)
        
        # Returns a random placement out of all possible moves
        else:
            return choice(possible_moves(self.game.board, self.color))

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)
