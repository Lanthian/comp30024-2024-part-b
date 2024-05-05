from __future__ import annotations
"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from math import inf, sqrt, log
from random import choice

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
        self.model = MCTS(1, self.game)

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
            # return ab(self.game, self.color, 2, h3)
            # return mcts(self.game)
            # self.model = MCTS(1, self.game)
            
            # print("=================================")
            # print(self.model.root.game)
            # print(self.model.root.move)
            # print(self.model.root.parent)
            # print(self.model.root.sub)

            self.model.new_root(self.game)
            # print(self.game in self.model.seen)
            # print(self.model.find_node(self.game))
            # self.model.diagnose()
            # print(self.model.children[self.model.root])
            # game move parent sub
            # print("=================================")
            # print(self.model.root.game)
            # print(self.model.root.move)
            # print(self.model.root.parent)
            # print(self.model.root.sub)
            print(len(self.model.seen))
            for _ in range(10):
                self.model.train()
            return self.model.choose_move(self.model.root)

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


# python -m referee agent agent         todo/temp
# === MCTS WIP HERE === - todo / temp

class Node():
    parent: Node | None
    sub: set['Node'] | None                 # Avoid regenerating children

    game: Gamestate
    move: PlaceAction

    def __init__(self, game: Gamestate, move: PlaceAction | None = None, 
                 parent: Node | None = None):
        self.parent = parent
        self.sub = None
        self.move = move
        self.game = game

    def all_children(self, monte: MCTS) -> set['Node']:
        """Avoid ever generating move and child state again by storing in MCTS 
        dictionary and locally in self.sub set. Does not alter parent / move of 
        already seen gamestates in MCTS."""
        # Only generate children if not yet done 
        # print("here's the problem")
        # if self.sub == None:
        self.sub = set()
        # print("lll")
        clr = self.game.current
        # Add all children states to node
        for move in possible_moves(self.game.board, clr):
            sub_game = self.game.child(move, clr)
            # Don't store in mcts if already existant
            if sub_game not in monte.seen:
                s = Node(sub_game, move, self)
                monte.register(s)
            self.sub.add(monte.seen[sub_game])
            
        return self.sub
    
    def item(self) -> PlaceAction:
        return self.move


class MCTS():
    # -- summarised from the lecture notes --
    #selection: select way through tree until leaf node is found
    #expansion: add singular new child from above leaf node
    #simulation: from newly added node playout to terminal state 
    #               (don't add played out moves to search tree)
    #backpropagation: utilise terminal state outcome to update states from node
    #                   to root.

    """Work In Progress:
    A class defined to act as the interface / brains of a Monte Carlo Tree 
    Search algorithm, storing state occurence frequency and win rate for each 
    explored state.
    
    Heavily inspired by the code supplied by Luke Harold Miles (qpwo) found
    here: https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1."""
    N: dict[Node: int]                      # occurences
    U: dict[Node: int]                      # utility (wins)
    ucb1_c: float

    children: dict[Node: set[Node]]
    seen: dict[Gamestate: Node]     # Gamestate dictionary to search for nodes
    root: Node

    def diagnose(self):
        print("VVVVVVVVVVVVVVVVVV")
        print(self.N)
        print(self.U)
        print(len(self.children))
        print(len(self.seen))
        print(self.root)
        print("^^^^^^^^^^^^^^^^^^")

    def __init__(self, c: float, base: Gamestate):
        # todo - abstract this code away from Gamestate
        self.ucb1_c = c 

        self.N = {}
        self.U = {}
        self.children = {}
        self.seen = {}

        # Immediately expand 
        self.root = self.find_node(base)
        self.expand(self.root)
        # todo - work here needs to be done to ensure count of plays aren't lost


    def select(self, state: Node) -> Node:        
        # Linearly (in relation to tree depth) walk through states until 
        # unexplored or end state found
        while True:
            # Check for new unexplored state
            if state not in self.children: return state
            # And check for terminal state (no following children)
            elif len(self.children[state]) == 0: return state
            
            # Check if there exists an unexpanded child of current state
            for child in self.children[state]:
                if child not in self.children:
                    return child
            
            # Otherwise step down a level
            state = self.step_down(state)

    def expand(self, state: Node):
        # Skip state if already expanded
        if state in self.children: return

        # Add to seen dictionary if first sighting
        if state.game not in self.seen:
            self.register(state)

        # Otherwise enqueue children to MCTS and prepare count dictionaries
        self.children[state] = state.all_children(self)

    def simulate(self, node: Node) -> ValWrap:
        """Returns a terminal node value wrapped by termination condition:
        1 if win, -1 if loss, 0 if draw."""
        # todo - abstract this code away from Gamestate
        # Check if terminal state reached (turn count or no remaining moves)
        if node.game.turn == TURN_CAP:
            # Calculate winner by tile count here - bound between [-1,1]
            scoring = min(max(h1(node.game, node.game.current),-1),1)
            return ValWrap(scoring, node)
        
        
        # Generate or access already generated children
        p = node.all_children(self)
        # Loss if no moves left
        if len(p) == 0:
            return ValWrap(-1, node)

        # Terminal not reached - choose a random successor somehow
        # Tuple used to convert set into iterable (for `choice` here)
        rdm_child = choice(tuple(p)) # todo - temp

        # Inverse score for recursively deeper child state
        x = self.simulate(rdm_child)
        x.invert()
        return x

    def backpropagate(self, result: int, state: Node | None):
        # Check if at the top (no further backpropagation needed)
        if state == None:
            return
        
        # Update state/node success
        self.N[state] += 1
        self.U[state] += result
        
        self.backpropagate(1-result, state.parent)


    def step_down(self, state: Node) -> Node:
        """Finds all children nodes from node `state` and returns the max node
        according to UCB1 algorithm with MCTS' `ucb1_c` constant. `state` must 
        NOT be a terminal node of tree (assert len(state.all_children(self)) > 0)"""
        # Value wrap with UCB1 value and list all children nodes
        l = [ValWrap(self.UCB1(child), child) for child in state.all_children(self)]
        # todo - temp
        print([i.val for i in l])
        print([f"{self.N[x]}-{self.U[x]}" for x in state.all_children(self)])
        print("--")
        return max(l).item
                
    def UCB1(self, node: Node) -> float | None:
        # Ensure root node is not used here
        if node.parent == None: return None

        n = self.N[node]
        exploit = self.U[node] / n
        # explore = sqrt(log(self.N[node.parent], n) / n)
        explore = sqrt(log(n) / n)
        return exploit + self.ucb1_c * explore


    def train(self):
        leaf = self.select(self.root)
        self.expand(leaf)
        result = self.simulate(leaf)
        
        # Handle win, loss, draw differently; currently treat a tie as a win
        match result.val:
            case -1: v = 0
            case 1: v = 1
            case 0: v = 1
        self.backpropagate(v, result.item)


    def choose_move(self, relative_root: Node) -> Action | None:
        # Training done - return most commonly explored node
        best = None
        n = 0
        
        # Only need to check children of root node as maximising occurence
        for node in self.children[relative_root]:
            # Skip unexplored children nodes
            if node not in self.N: continue

            rate = self.N[node]
            if rate > n:
                n = rate
                best = node

        # Failsafe in case 0 training has been done (return None)
        if best == None: return None
        # Otherwise return best move    
        return best.item()
    
    def find_node(self, game: Gamestate) -> Node:
        """Returns an existing node if generated & explored, otherwise generates 
        and returns it as a new root. Done to avoid duplicating tree spreads."""
        if game not in self.seen:
            self.register(Node(game))
        return self.seen[game]
    
    def register(self, node: Node):
        # Only call on nodes not already seen
        self.seen[node.game] = node
        self.N[node] = 0
        self.U[node] = 0

    def new_root(self, game: Gamestate):
        # Update root with new gamestate (turns have passed since last call)
        self.root = self.find_node(game)
        self.root.parent = None
        self.children = {}
        # self.children.clear()
        self.expand(self.root)
        # print(f"E -> {self.root.all_children(self)}")


def mcts(game: Gamestate) -> Action:
    # look into storing mcts constructed between moves, so that it gets smarter 
    # and deeper the longer the game goes on - todo via find_node and moving 
    # MCTS() elsewhere
    model = MCTS(1, game)
    for _ in range(10):
        model.train()
    return model.choose_move(model.root)
    

# python -m referee agent agent         t   odo/temp
