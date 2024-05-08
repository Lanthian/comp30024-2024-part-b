"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module.
Agent selects next move via an alpha-Beta pruned search algorithm paired with 
heuristics to find next optimal path."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from math import inf

from agent.control import possible_moves, first_move
from agent.gamestate import Gamestate, flatten_board
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
    seen: dict[str: list[Action]]
    # todo - perhaps implement a method to clear past seen to free space -
    #        could be done in .update() method. Store seen items in prioritydict
    #        based on turn?

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        All setup and/or precomputation is done here.
        """
        self.first_move =True
        self.color = color
        self.game = Gamestate()
        self.seen = {}

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. Always returns an action object. 
        """
        if self.first_move:
            self.first_move=False

            match self.color:
                case PlayerColor.RED:
                    return first_move(self.game.board)
                case PlayerColor.BLUE:
                    return first_move(self.game.board)
        
        else:
            # Intelligently select next move
            a = ab(self, 2, h3)
            print(len(self.seen))
            return a

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)


def ab(agt: Agent, depth: int, heu) -> Action | None:
    """The origin point for an alpha-beta pruning minimax approach to searching
    through next possible moves for a gamestate `agt.game`. Remaining max 
    recursions are determined from `depth`, and bottom nodes are evaluated 
    according to the heuristic `heu` for optimal color `agt.color`.
    Returns an Action, None if depth too shallow or no possible moves."""
    # Can't search less than 1
    if depth <= 0: return None

    a = ValWrap(-inf, None)
    b = ValWrap(inf, None)
    return sub_ab(True, agt.game, None, agt.color, depth, heu, agt, a, b).item

def sub_ab(max_flag: bool, game: Gamestate, move: Action, player: PlayerColor, 
           depth: int, heu, agt: Agent, a: ValWrap, b: ValWrap) -> ValWrap:
    """ab() sub-function. Maximises or minimises outcome depending on 
    alternating depth level. Equivalent to ab_max if `max_flag` is set to True, 
    ab_min if set to False. Returns a ValWrap-ed Action."""
    # -- Check cutoff states --
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
        flat_b = flatten_board(game.board)
        # Avoid recalculating possible moves by storing game state in `seen`
        if flat_b not in agt.seen: 
            agt.seen[flat_b] = possible_moves(game.board, game.current)
        next_moves = agt.seen[flat_b]

        # If no moves remaining, reflect this WIN/LOSS from player's perspective
        if len(next_moves) == 0:
            if game.current == player: return ValWrap(LOSS, move)
            else: return ValWrap(WIN, move)
            

        # Otherwise, proceed with max/min value search depending on turn
        for p in next_moves:
            s = game.child(p,game.current)
            m = p if (move == None) else move

            # Update maximum possible outcome if flag true
            if max_flag:
                a = max(a, sub_ab(False, s, m, player, depth-1, heu, agt, a, b))
                if a.val >= b.val: return b
            # Update minimum possible outcome if flag false
            else:
                b =  min(b, sub_ab(True, s, m, player, depth-1, heu, agt, a, b))
                if b.val <= a.val: return a

        # Return a / b if no turnover
        if max_flag: return a
        else: return b
