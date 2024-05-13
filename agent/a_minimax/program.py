"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module.
Agent selects next move via minimax search algorithm paired with heuristics to 
find next optimal path."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from agent.control import first_move, possible_moves
from agent.gamestate import Gamestate
from agent.heuristics import *
from agent.valwrap import ValWrap

from referee.game import Action, PlayerColor, MAX_TURNS

# === Constants ===
WIN = 10000
LOSS = -WIN


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
        self.first_move = True
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
        
        else:
            # Intelligently select next move
            return minimax(self.game,2,h1)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)


def minimax(game: Gamestate, depth: int, heu) -> Action | None:
    """Origin point for default minimax approach to searching through next
    possible moves for a gamestate `game`. Remaining max recursions are 
    determined from `depth`, and bottom nodes evaluated according to the
    heuristic `heu`.
    Returns an Action, None if depth too shallow."""
    # Can't search less than 1
    if depth <= 0: return None

    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)
        if len(moves) == 0: return None

        # Recurse down this level to depth `depth`, returning best move
        m = max([sub_minimax(game.child(p,game.current), p, game.current, 
                             depth-1, heu) for p in moves])
        return m.item

def sub_minimax(game: Gamestate, move: Action, player: PlayerColor, 
                depth: int, heu) -> ValWrap:
    """minimax() sub-function. Depending on players turn, either maximises
    or minimises outcome. Returns a ValWrap-ed Action."""
    if depth == 0:
        # Bottom reached
        return ValWrap(heu(game, player), move)
    
    if game.turn > MAX_TURNS:
        # Last move was final turn - player with most tokens wins
        if game.counts[game.current] > game.counts[game.current.opponent]:
            return ValWrap(WIN, move)
        else: return ValWrap(LOSS, move)

    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)

        # If no moves remaining, reflect this WIN/LOSS from player's perspective
        if len(moves) == 0:
            if game.current == player: return ValWrap(LOSS, move)
            else: return ValWrap(WIN, move)

        # Proceed with minimum or maximum value depending on turn
        heus = [sub_minimax(game.child(p,game.current), move, 
                        player, depth-1, heu) for p in moves]

        if game.current == player:
            # Player chooses highest next value move
            return max(heus)
        else: 
            # Opponent chooses lowest next value move
            return min(heus)
