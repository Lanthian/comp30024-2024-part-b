from __future__ import annotations
"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .prioritydict import PriorityDict
from .control import possible_moves, make_place
from .utils import render_board     # todo/temp

# python -m referee agent agent     todo/temp
# python -m referee agent agent_rdm
# python -m referee agent_rdm agent
# python -m referee agent_rdm agent_rdm

class Gamestate:
    """
    Dataclass to represent a state of the game, storing additional information 
    to reduce calculation time.
    """
    # Board represented as a sparse dictionary to save space
    board: dict[Coord, PlayerColor] = {} 
    current: PlayerColor = PlayerColor.RED      # Red starts
    # todo - heuristic value stored here perhaps?

    # Below count done as to minimise recalculation of dictionary elements
    counts: dict[PlayerColor, int] = {PlayerColor.RED: 0, PlayerColor.BLUE: 0}


    def move(self, action: Action, color: PlayerColor):
        make_place(self.board, action, color)

        # todo - not a good implementation atm, just temporary
        self.counts[PlayerColor.RED] = 0
        self.counts[PlayerColor.BLUE] = 0

        for clr in self.board.values():
            self.counts[clr] += 1

        self.current = color.opponent

    def copy(self) -> Gamestate:
        new = Gamestate()
        new.board = self.board.copy()
        new.current = self.current
        new.counts = self.counts.copy()
        return new

    def child(self, action: Action, color: PlayerColor) -> Gamestate:
        new = self.copy()
        new.move(action, color)
        return new


class Agent:
    """
    This class is the "entry point" for an agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool=True
    color: PlayerColor
    rival: PlayerColor

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        All setup and/or precomputation is done here.
        """
        
        self.color = color
        self.rival = color.opponent

        self.game = Gamestate()


    """ todo; Lanthian - I think sparse game board is better here, but I've 
    commented the below out instead of deleting it just in case """
    #     self.initialize_game_board()

    # def initialize_game_board(self):
    #     """
    #     Initialize or reset the game board to an empty state.
    #     """
    #     for r in range(BOARD_N):
    #         for c in range(BOARD_N):
    #             self.board[Coord(r,c)] = None
    #             # sparse game board might be better here, but we'll see


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. Always returns an action object. 

        Need to update this for action
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        
        if self.first_move:
            # todo - First move approach will need to be designed still
            self.first_move=False

            match self.color:
                case PlayerColor.RED:
                    print("Testing: RED is playing a PLACE action")
                    #nextMove = self.getNextMove(self.color)
                    return PlaceAction(
                        Coord(5, 4), Coord(3, 4), Coord(4, 3), Coord(4, 4)
                    )
                case PlayerColor.BLUE:
                    print("Testing: BLUE is playing a PLACE action")
                    #nextMove = self.getNextMove(self.color)
                    return PlaceAction(
                        Coord(2, 3), Coord(2, 4), Coord(2, 5), Coord(2, 6)
                    )
        
        # todo - temporary, unintelligent implementation
        else:

            # Generate all possible next moves, greedy pick based on heuristic
            pd = PriorityDict()
            pd.clear()   # todo/temp - needed as new PD not actually generated?

            return minimax(self.game,1,h1)

            # for move in possible_moves(self.game.board, self.color):
            #     child = self.game.child(move, self.color)
            #     h = -h1(child, self.color)  # Inverting for use in Priority Dict
            #     pd.put(h, move) # insert all moves as equal cost for now...

            # return pd.get()


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)
        
        # todo/temp - temporary printing of update call
        print(f"Testing: {color} played PLACE action: " +
              f"{", ".join([str(x) for x in action.coords])}")


def h1(game: Gamestate, color: PlayerColor) -> int:
    """Returns the integer token count difference between opponent and player 
    `color` in a Gamestate `game`. A larger number is better for player."""
    return game.counts[color] - game.counts[color.opponent]

def h2(game: Gamestate, color: PlayerColor) -> int:
    """Returns the interger possible move difference between opponent and player
    `color` in a Gamestate `game`. A larger number is better for player."""
    # todo / temp - wayyyy too slow at the moment. Not feasible to check unless 
    # a faster method of generating moves is found
    a = len(possible_moves(game.board, color))
    b = len(possible_moves(game.board, color.opponent))
    return a - b

# python -m referee agent agent         todo/temp


def sub_minimax(game: Gamestate, move: Action, player: PlayerColor, depth: int, heu) -> tuple[int, Action]:
    WIN = 10000
    LOSS = -WIN

    if depth == 0:
        # Bottom reached
        return (heu(game, player), move)
    
    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)

        # If no moves remaining, reflect this WIN or LOSS condition from player perspective
        if moves == 0:
            if game.current == player: return (LOSS, move)
            else: return (WIN, move)

        # Proceed with minimum or maximum value depending on turn
        heus = [sub_minimax(game.child(p,game.current), move, 
                        player, depth-1, heu) for p in moves]

        if game.current == player:
            # Player chooses highest next value move
            return max(heus)
        else: 
            # Opponent chooses lowest next value move
            return min(heus)
        
def minimax(game: Gamestate, depth: int, heu) -> Action | None:
    if depth == 0: return None

    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)
        if len(moves) == 0: return None

        ACTION_INDEX = 1
        m = max([sub_minimax(game.child(p,game.current), p, game.current, depth-1, heu) for p in moves])
        return m[ACTION_INDEX]
    