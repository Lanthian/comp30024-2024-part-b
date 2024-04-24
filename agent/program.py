# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .prioritydict import *
# from .tetrominoes import *
from .control import *


class Gamestate:
    """
    Dataclass to represent a state of the game, storing additional information 
    to reduce calculation time.
    """
    # board representation
    board: dict[Coord, PlayerColor] = {} # Dictionary to maintain the game state
    current: PlayerColor = PlayerColor.RED # Red starts
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

        self.current = other_color(color)


# python -m referee agent agent                 todo / temp
class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """
    first_move: bool=True
    color: PlayerColor
    rival: PlayerColor

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        
        self.color = color
        self.rival = other_color(color)

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
            for move in possible_moves(self.game.board, self.color):
                # h = heuristic(self.game, move, self.color)
                h = self.game.counts[other_color(self.color)] - self.game.counts[self.color]
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
        self.game.move(action, color)
        
        c1, c2, c3, c4 = action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
        

def heuristic(game: dict[Coord, PlayerColor],
              move: PlaceAction,
              player: PlayerColor) -> float:
    # todo - flesh this code out
    # new_board = make_place(board.copy(), move, player)

    # match player:
    #     case PlayerColor.RED:
    #         opposite = PlayerColor.BLUE
    #     case PlayerColor.BLUE:
    #         opposite = PlayerColor.RED

    # a = len(possible_moves(new_board, player))
    # b = len(possible_moves(new_board, opposite))
    # return a - b
    return 0


def other_color(color: PlayerColor) -> PlayerColor:
    # colors = [PlayerColor.RED, PlayerColor.BLUE]
    # return [c for c in colors if c != color][0]
    match color:
        case PlayerColor.RED:  return PlayerColor.BLUE
        case PlayerColor.BLUE: return PlayerColor.RED
