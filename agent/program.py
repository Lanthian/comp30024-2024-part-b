"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from math import inf

from referee.game import Action, Coord, PlaceAction, PlayerColor, Direction

from .prioritydict import PriorityDict
from .control import possible_moves, make_place, first_move
from .utils import render_board     # todo/temp
from .valwrap import ValWrap

# === Constants ===
WIN = 10000
LOSS = -WIN
TURN_CAP = 150

# === Terminal prompts ===
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
    turn: int = 1                               # First turn is turn 1

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


class Agent:
    """
    This class is the "entry point" for an agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool=True
    color: PlayerColor

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        All setup and/or precomputation is done here.
        """
        
        self.color = color
        self.game = Gamestate()

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
        
        else:
            # Intelligently select next move
            # return minimax(self.game,1,h1)     # todo - too inefficient to run
            return ab(self.game, self.color, 2, h3)

            # # Generate all possible next moves, greedy pick based on heuristic
            # pd = PriorityDict()
            # pd.clear()   # todo/temp - needed as new PD not actually generated?
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

        # todo - switch Agents h or move making strategy of choice depending on 
        #        turn count here.
        
        # todo/temp - temporary printing of update call
        print(f"Testing: {color} played PLACE action: " +
              f"{", ".join([str(x) for x in action.coords])}")



def h1(game: Gamestate, color: PlayerColor) -> int:
    """Returns the integer token count difference between opponent and player 
    `color` in a Gamestate `game`. A larger number is better for player.
    Goal: Maximise difference in player tiles on board."""
    return game.counts[color] - game.counts[color.opponent]

def h2(game: Gamestate, color: PlayerColor) -> int:
    """Returns the interger possible move difference between opponent and player
    `color` in a Gamestate `game`. A larger number is better for player.
    Goal: Maximise difference in remaining possible moves between players."""
    # todo / temp - wayyyy too slow at the moment. Not feasible to check unless 
    # a faster method of generating moves is found
    a = len(possible_moves(game.board, color))
    b = len(possible_moves(game.board, color.opponent))
    return a - b

def h3(game: Gamestate, color: PlayerColor) -> float:
    """Returns the float neighbouring air tile difference between opponent and
    player `color` in a Gamestate `game`. A larger number is player favoured. 
    Balance between tiles can be altered by changing a & b values.
    Goal: Minimise possible placement tiles opponent has (suffocate them)
      while maximising a players own possible placement tiles."""
    blank_nbrs = {color: set(), color.opponent: set()}
    a = 0.1
    b = 1

    # Iterate through all tiles and their neighbours
    for (coord, clr) in game.board.items():
        for dir in [d.value for d in Direction]:
            new = Coord.__add__(coord, dir)
            # If neighbour is empty air, add one to relevant tally
            if new not in game.board:
                blank_nbrs[clr].add(new)

    return a*len(blank_nbrs[color]) - b*len(blank_nbrs[color.opponent])


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
    
    else: 
        # Find next level of the tree of possible states
        moves = possible_moves(game.board, game.current)

        # If no moves remaining, reflect this WIN/LOSS from player's perspective
        if len(moves) == 0:
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


def ab(game: Gamestate, player: PlayerColor, depth: int, heu) -> Action | None:
    """The origin point for an alpha-beta pruning minimax approach to searching
    through next possible moves for a gamestate `game`. Remaining max recursions
    are determined from `depth`, and bottom nodes are evaluated according to the
    heuristic `heu` for optimal color `player`.
    Returns an Action, None if depth too shallow or no possible moves."""
    # Can't search less than 1
    if depth <= 0: return None

    a = ValWrap(-inf, None)
    b = ValWrap(inf, None)
    return sub_ab(True, game, None, player, depth, heu, a, b).item

def sub_ab(max_flag: bool, game: Gamestate, move: Action, player: PlayerColor, 
                depth: int, heu, a: ValWrap, b: ValWrap) -> ValWrap:
    """ab() sub-function. Maximises or minimises outcome depending on 
    alternating depth level. Equivalent to ab_max if `max_flag` is set to True, 
    ab_min if set to False. Returns a ValWrap-ed Action."""
    # Check cutoff states
    if depth == 0:
        # Bottom reached
        return ValWrap(heu(game, player), move)
    else: 
        # Find next level of the tree of possible states
        next_moves = possible_moves(game.board, game.current)
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
                a = max(a, sub_ab(False, s, m, player, depth-1, heu, a, b))
                if a.val >= b.val: return b
            # Update minimum possible outcome if flag false
            else:
                b =  min(b, sub_ab(True, s, m, player, depth-1, heu, a, b))
                if b.val <= a.val: return a

        # Return a / b if no turnover
        if max_flag: return a
        else: return b

"""

# def mcts(game: Gamestate, heu) -> Action:
#     # -- from the lecture notes --
#     #selection: select way through tree until leaf node is found
#     #expansion: add singular new child from above leaf node
#     #simulation: from newly added node playout to terminal state 
#     #               (don't add played out moves to search tree)
#     #backpropagation: utilise terminal state outcome to update states from node
#     #                   to root.

#     # useful demo: https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
#     # by Luke Harold Miles (qpwo) - https://gist.github.com/qpwo
#     tree = dict()


#     for i in range(10):

#         # for move in possible_moves(self.game.board, self.color):

#         child_tree = dict()
    

class Node():
    parent: 'Node' | None
    children: set['Node']

    game: Gamestate
    playouts: int = 0
    wins: int = 0

    def __init__(self, game: Gamestate, parent: 'Node' | None = None):
        self.parent = parent
        self.game = game


class MCTS():
    player: PlayerColor

    state_occurences = dict()
    state_wins = dict()
    tree: Node

    def __init__(self, base: Gamestate):
        self.tree = Node(base)

        self.state_occurences[base] = 0
        self.state_wins[base] = 0


    def select(self) -> Node:
        # select from self.tree somehow

    def expand(self):


    def playout(self, game: Gamestate):
        # Check if terminal state reached
        if game.turn == TURN_CAP:
            # Calculate winner by tile count here - bound between [-1,1]
            return min(max(h1(game, self.player),-1),1)
        
        p = possible_moves(game.board, game.current)
        if len(p) == 0:
            # If no moves left on players turn, loss. 
            if game.current == self.player: return -1
            # If no moves left on rivals turn, win.
            else: return 1

        # Terminal not reached - choose a successor somehow
        move = p[0]
        self.playout(game.child(move, game.current))


    def backpropagate(self, result, state: Node | None):
        if state == None:
            # Reached the top, no further backpropagation needed

        self.backpropagate(self, result, state.parent)


    def train(self, condition):
        while condition:
            leaf = self.select()
            child = self.expand(leaf)
            result = self.playout(child)
            self.backpropagate(result, child)

"""

# python -m referee agent agent         todo/temp
