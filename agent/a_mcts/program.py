from __future__ import annotations
"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module.
Agent selects next move via a Monte Carlo Tree Search algorithm paired to find 
next optimal move."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from math import inf, log, sqrt
from random import choice

from agent.control import possible_moves, first_move
from agent.gamestate import Gamestate, flatten_board
from agent.heuristics import *
from agent.valwrap import ValWrap

from referee.game import Action, PlaceAction, PlayerColor, MAX_TURNS

# === Constants ===
ITERATIONS = 10
C = 0       # currently set to massively prefer exploitation over exploration


class Agent:
    """
    This class is the "entry point" for an agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool
    color: PlayerColor
    # model: MCTS | None              # None until initialised

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        All setup and/or precomputation is done here.
        """
        self.first_move = True
        self.color = color
        self.game = Gamestate()
        self.model = None

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
            # Prepare model for playing on 'second move'
            if self.model == None: self.model = MCTS(C, self.game)

            # Train model set amount of times and select next move
            self.model.train(ITERATIONS)
            return self.model.choose_move(self.model.root)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)
        # If >= second move for player, update Monte Carlo Tree with new root
        if self.model != None: self.model.new_root(self.game)


class Node():
    """A class to act as a multi-directional linked node in a tree of precursor
    and successor states. Specialised to manage the Tetress Gamestate and 
    PlaceAction types."""
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
        # Only generate children if not yet done so
        if self.sub == None:
            self.sub = set()

            clr = self.game.current
            # Add all children states to node
            for move in possible_moves(self.game.board, clr):
                sub_game = self.game.child(move, clr)
                # Don't store in mcts if already generated
                f = flatten_board(sub_game.board)
                if f not in monte.seen:
                    s = Node(sub_game, move, self)
                    monte.register(s, f)
                self.sub.add(monte.seen[f])
        else: monte.reuse_count += 1
            
        return self.sub
    
    def item(self) -> PlaceAction:
        return self.move


class MCTS():
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
    seen: dict[str: Node]     # Flat board dictionary to search for nodes
    root: Node

    def __init__(self, c: float, base: Gamestate):
        """
        The initiation point for handling a Monte Carlo Tree Search approach to 
        searching through next possible moves from an initial Gamestate `base`. 
        Exploitation vs exploration constant in ubc1 algo defined by `c` param.
        """
        # todo - abstract this code away from Gamestate
        self.root = Node(base)
        self.ucb1_c = c 

        self.N = {}
        self.U = {}
        self.children = {}
        
        self.seen = {}
        self.reuse_count = 0

        # Immediately expand 
        self.expand(self.root)


    def select(self, state: Node) -> Node:     
        """Step 1: Select way through tree until leaf node is found"""   
        # Linearly (in relation to tree depth) walk through states until 
        # unexplored or end state found. 
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
        """Step 2: Expand - add singular new child from above leaf node"""
        # Skip state if already expanded
        if state in self.children: return

        # Add to seen dictionary if first sighting
        f = flatten_board(state.game.board)
        if f not in self.seen:
            self.register(state, f)

        # Otherwise enqueue children to MCTS and prepare count dictionaries
        self.children[state] = state.all_children(self)

    def simulate(self, node: Node) -> ValWrap:
        """Step 3: Simulate playout with newly added node to terminal state, not 
        yet adding child nodes to playout tree.
        
        Returns:
          a terminal node value wrapped by termination condition:
          1 if win, -1 if loss, 0 if draw."""
        # todo - abstract this code away from Gamestate
        # Check if terminal state reached (turn count or no remaining moves)
        if node.game.turn == MAX_TURNS:
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
        rdm_child = choice(tuple(p))

        # Inverse score for recursively deeper child state
        x = self.simulate(rdm_child)
        x.invert()
        return x

    def backpropagate(self, result: int, state: Node):
        """Step 4: utilise terminal state outcome to update states from node
        to root, adding newly seen nodes into playout tree."""
        # Check if by some error state is unset
        if state == None:
            # print("ERROR: Unset node backpropagated to somehow. Investigate.")
            return

        # Update state/node success
        self.N[state] += 1
        self.U[state] += result

        # Check if at the top (no further backpropagation needed)
        if state == self.root:
            return
        # Otherwise backtrack further
        self.backpropagate(1-result, state.parent)


    def step_down(self, state: Node) -> Node:
        """Finds all children nodes from node `state` and returns the max node
        according to UCB1 algorithm with MCTS' `ucb1_c` constant. `state` must 
        NOT be a terminal node of tree - assert the below before calling:
            len(state.all_children(self)) > 0"""
        # Value wrap with UCB1 value and list all children nodes
        l = [ValWrap(self.UCB1(child), child) 
             for child in state.all_children(self)]

        # # todo - temp
        # print([i.val for i in l])
        # print([f"{self.N[x]}-{self.U[x]}" for x in state.all_children(self)])
        # print("--")

        return max(l).item
                
    def UCB1(self, node: Node) -> float | None:
        """UCB1 algorithm, balanced by MCTS' `ucb1_c` constant. Returns `None`
        if used on a tree root node, a float otherwise."""
        # Ensure root node is not used here
        if node.parent == None: return None
        # And child node scouted has been expanded
        if node not in self.N: return inf

        n = self.N[node]
        # If n == 0 (not yet explored somehow), prioritise exploiting it
        exploit = self.U[node] / n if n != 0 else inf
        # explore = sqrt(log(self.N[node.parent], n) / n)
        explore = sqrt(log(n) / n)
        return exploit + self.ucb1_c * explore


    def train(self, n: int=1):
        """Simulate through an MCTS search `n` times, backpropagating and 
        updating all traveled nodes in path."""
        for _ in range(n):
            leaf = self.select(self.root)
            self.expand(leaf)
            result = self.simulate(leaf)
            
            # Handle win, loss, draw differently; currently treat a tie as a win
            match result.val:
                case -1: v = 0
                case 0: v = 1
                case 1: v = 1
            self.backpropagate(v, result.item)
            # print(f"Stored v Reuse: {len(self.seen)} . {self.reuse_count}")


    def choose_move(self, relative_root: Node) -> Action | None:
        """Return best move from node `relative_root` according to most explored 
        child node of `relative_root`. Returns `None` if no children exist for
        `relative_root` node, or a move of type `Action` if otherwise."""
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
        f = flatten_board(game.board)
        if f not in self.seen:
            self.register(Node(game), f)
        return self.seen[f]         # node of game
    
    def register(self, node: Node, flat_b: str | None = None):
        """Begins tracking of new Node `node` in MCTS. Only call on nodes not
        already seen."""
        if flat_b == None: flat_b = flatten_board(node.game.board)
        self.seen[flat_b] = node
        self.N[node] = 0
        self.U[node] = 0

    def new_root(self, game: Gamestate):
        """Update MCTS with new Gamestate `game` at the root - turns have passed
        and a new root is present."""
        self.root = self.find_node(game)
        # self.children.clear()
        # self.expand(self.root)
