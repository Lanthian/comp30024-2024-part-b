from __future__ import annotations
"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass
from functools import total_ordering

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .prioritydict import PriorityDict
from .control import possible_moves, make_place, first_move
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


@dataclass(frozen=True, slots=True)
@total_ordering
class ValWrap():
    """
    Storage of a Gamestate alongside a heuristic int so that gamestates can be
    compared.
    """
    val: int                    # ordering value to compare against other nodes
    item: Gamestate | None

    # def __init__(self, value: int, game: Gamestate | None = None):
    #     """
    #     Constructor method for fleshing out a node. Gamestate has value `None`
    #     by default.
    #     """
    #     self.val = value
    #     self.item = game

    def __eq__(self, other: ValWrap):
        return self.val == other.val
    
    def __lt__(self, other: ValWrap):
        return self.val < other.val


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
        
        if self.first_move:
            # todo - First move approach will need to be designed still
            self.first_move=False

            match self.color:
                case PlayerColor.RED:
                    print("Testing: RED is playing a PLACE action")
                    #nextMove = self.getNextMove(self.color)
                    # return PlaceAction(Coord(5, 4), Coord(3, 4), Coord(4, 3), Coord(4, 4))
                    return first_move(self.game.board)
                case PlayerColor.BLUE:
                    print("Testing: BLUE is playing a PLACE action")
                    #nextMove = self.getNextMove(self.color)
                    # return PlaceAction(Coord(2, 3), Coord(2, 4), Coord(2, 5), Coord(2, 6))
                    return first_move(self.game.board)
        
        # todo - temporary, unintelligent implementation
        else:

            # Generate all possible next moves, greedy pick based on heuristic
            pd = PriorityDict()
            pd.clear()   # todo/temp - needed as new PD not actually generated?

            # return minimax(self.game,2,h1)        todo - to inefficient to run
            # return ab(self.game, self.color, 1, h1)

            for move in possible_moves(self.game.board, self.color):
                child = self.game.child(move, self.color)
                h = -h1(child, self.color)  # Inverting for use in Priority Dict
                pd.put(h, move) # insert all moves as equal cost for now...

            return pd.get()


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


# def heuristic(game: dict[Coord, PlayerColor],
#               move: PlaceAction,
#               player: PlayerColor) -> float:
#     # todo - flesh this code out
#     # new_board = make_place(board.copy(), move, player)

#     # a = len(possible_moves(new_board, player))
#     # b = len(possible_moves(new_board, player.opponent))
#     # return a - b
#     return 0

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


# todo - temp, fix this up so it's neater, more sensible, and more efficient.

def sub_minimax(game: Gamestate, move: Action, player: PlayerColor, 
                depth: int, heu, a, b) -> tuple[int, Action]:
    VAL_INDEX = 0
    WIN = 10000
    LOSS = -WIN

    if depth == 0:
        # Bottom reached
        return (heu(game, player), move)
    
    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)

        # If no moves remaining, reflect this WIN or LOSS condition from player perspective
        if len(moves) == 0:
            if game.current == player: return (LOSS, move)
            else: return (WIN, move)

        # Proceed with minimum or maximum value depending on turn
        heus = [sub_minimax(game.child(p,game.current), move, 
                        player, depth-1, heu) for p in moves]

        if game.current == player:
            # Player chooses highest next value move
            return max(heus, key=lambda x: x[VAL_INDEX])
        else: 
            # Opponent chooses lowest next value move
            return min(heus, key=lambda x: x[VAL_INDEX])
        
def minimax(game: Gamestate, depth: int, heu) -> Action | None:
    VAL_INDEX = 0
    ACTION_INDEX = 1
    
    # Can't search less than 1
    if depth <= 0: return None

    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)
        if len(moves) == 0: return None

        # Recurse down this level to depth `depth`, returning best move
        m = max([sub_minimax(game.child(p,game.current), p, game.current, 
                             depth-1, heu, -10000, 10000) for p in moves], 
                             key=lambda x: x[VAL_INDEX])
        return m[ACTION_INDEX]

# python -m referee agent agent         todo/temp


# todo - wip
def ab(game: Gamestate, player: PlayerColor, depth: int, heu) -> Action:
    a = ValWrap(-100000, None)
    b = ValWrap(100000, None)
    return ab_max(game, None, player, depth, heu, a, b).item


def ab_max(game: Gamestate, move: Action, player: PlayerColor, 
                depth: int, heu, a: ValWrap, b: ValWrap) -> ValWrap:
    WIN = 10000
    LOSS = -WIN

    moves = []

    # Cutoff state
    if depth == 0:
        # Bottom reached
        return ValWrap(heu(game, player), move)
    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)
        # If no moves remaining, reflect this WIN or LOSS condition from player perspective
        if len(moves) == 0:
            if game.current == player: return ValWrap(LOSS, move)
            else: return ValWrap(WIN, move)


        # Otherwise, proceed with maximum value depending on turn
        heus = []
        for p in moves:
            s = game.child(p,game.current)
            a = max(a, ab_min(game, move, player, depth-1, heu, a, b))
            if a.val >= b.val: return b
        return a
    
def ab_min(game: Gamestate, move: Action, player: PlayerColor, 
                depth: int, heu, a: ValWrap, b: ValWrap) -> ValWrap:
    WIN = 10000
    LOSS = -WIN

    # Cutoff state
    if depth == 0:
        # Bottom reached
        return ValWrap(heu(game, player), move)
    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)
        # If no moves remaining, reflect this WIN or LOSS condition from player perspective
        if len(moves) == 0:
            if game.current == player: return ValWrap(LOSS, move)
            else: return ValWrap(WIN, move)


        # Otherwise, proceed with minimum value depending on turn
        heus = []
        for p in moves:
            s = game.child(p,game.current)
            b =  min(b, ab_max(game, move, player, depth-1, heu, a, b))
            if a.val >= b.val: return a
        return b
