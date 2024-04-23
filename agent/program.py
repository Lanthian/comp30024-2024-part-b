# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .prioritydict import *
# from .tetrominoes import *
from .control import *


""" class Gamestate:
    # board representation
    # current player
    # heuristic value
    # # below count done as to minimise recalculation of dictionary elements
    # count of red
    # count of blue """

# python -m referee agent agent                 todo / temp
class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool=True

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        
        self.color = color
        self.game_board = {}  # Dictionary to maintain the game state

    """ todo; Lanthian - I think sparse game board is better here, but I've 
    commented the below out instead of deleting it just in case """
    #     self.initialize_game_board()

    # def initialize_game_board(self):
    #     """
    #     Initialize or reset the game board to an empty state.
    #     """
    #     for r in range(BOARD_N):
    #         for c in range(BOARD_N):
    #             self.game_board[Coord(r,c)] = None
    #             # sparse game board might be better here, but we'll see


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 

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
                        Coord(5, 4), 
                        Coord(3, 4), 
                        Coord(4, 3), 
                        Coord(4, 4)
                    )
                case PlayerColor.BLUE:
                    print("Testing: BLUE is playing a PLACE action")
                    #nextMove = self.getNextMove(self.color)
                    return PlaceAction(
                        Coord(2, 3), 
                        Coord(2, 4), 
                        Coord(2, 5), 
                        Coord(2, 6)
                    )
        
        # todo - temporary, unintelligent implementation
        else:
            # Generate all possible next moves, greedy pick based on heuristic
            pd = PriorityDict()
            for move in possible_moves(self.game_board, self.color):
                h = heuristic(self.game_board, move, self.color)
                pd.put(h, move) # insert all moves as equal cost for now...

            return pd.get()


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 

        note: this updates internal state (non-printed one) for further move 
        calculation, game separately extracts board state to print visually 
        """
        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        make_place(self.game_board, action, color)
        
        c1, c2, c3, c4 = action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
        

def heuristic(board: dict[Coord, PlayerColor],
              move: PlaceAction,
              player: PlayerColor) -> float:
    # todo - flesh this code out
    return 0
