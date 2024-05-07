"""program.py: Supplies an `Agent` class to play Tetress in competition with 
another agent. Managed by the referee module.
Agent selects next move greedily depending on chosen heuristic."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from agent.control import first_move, possible_moves
from agent.gamestate import Gamestate
from agent.prioritydict import PriorityDict
from referee.game import Action, Coord, Direction, PlayerColor

# === Constants ===
WIN = 10000
LOSS = -WIN
TURN_CAP = 150


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
        """
        if self.first_move:
            self.first_move=False

            match self.color:
                case PlayerColor.RED:
                    return first_move(self.game.board)
                case PlayerColor.BLUE:
                    return first_move(self.game.board)
        
        else:
            # Generate all possible next moves, greedy pick based on heuristic
            pd = PriorityDict()
            for move in possible_moves(self.game.board, self.color):
                child = self.game.child(move, self.color)
                h = -h1(child, self.color)  # Inverting for use in Priority Dict
                pd.put(h, move)
            return pd.get()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Called by referee after valid agent turn. Update internal game state 
        according to affects of move `action` made.
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        self.game.move(action, color)


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
