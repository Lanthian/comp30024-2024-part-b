# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from .prioritydict import *
from .tetrominoes import *
from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
# from agent import tetrominoes_plus
# from agent import PriorityDict
# from agent import PriorityDict
# from agent import tetrominoes_plus


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
        self.initialize_game_board()

    def initialize_game_board(self):
        """
        Initialize or reset the game board to an empty state.
        """
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                self.game_board[Coord(r,c)] = None
                # sparse game board might be better here, but we'll see


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
        
        else:
            pd = PriorityDict()
            for move in possible_moves(self.game_board, self.color):
                pd.put(0, move) # insert all moves as equal cost for now...

            return pd.get()


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 

        note: this updates internal state (non-printed one) for further move calculation, game separately extracts board state 
        to print visually 
        """


        # There is only one action type, PlaceAction. 
        # Clear filled lines as necessary.
        make_place(self.game_board, action, color)
        
        c1, c2, c3, c4 = action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
        

def possible_moves(board: dict[Coord, PlayerColor], 
                   player: PlayerColor) -> list[PlaceAction]:
    """
    Takes a game `board` and a `player` defined by their PlayerColor and returns 
    all possible next moves for said player in the form of a list of 
    PlaceActions.
    """
    moves = set()
    for (coord, color) in board.items():
        if color == player:
            # duplicate moves generated and ignored here (possible improvement)
            moves.update(tetrominoes_plus(coord, set(board.keys())))

    return list(moves)


def free_cells(
    board: dict[Coord, PlayerColor], 
    target: Coord,
    axis: str
) -> int | None:
    """Takes a dictionary of board tokens `board`, a Coord `target`, and an 
    `axis` flag to determine which board axis is counted over. Utilises the fact 
    that the board is a sparse representation of tokens present by checking if 
    dict contains each axis coordinate.

    Returns:
        Either the count of free cells in target axis, or None if invalid `axis`
        flag supplied.
    """    
    # Find which axis is iterated over
    match axis:
        case "x" | "r" | "row":
            axis_iterator = lambda t: Coord(target.r, t)
        case "y" | "c" | "col":
            axis_iterator = lambda t: Coord(t, target.c)
        case _:
            print("ERROR free_cells: invalid axis specified.")
            return None

    free = BOARD_N
    # Subtract occupied cells to find free count
    for i in range(BOARD_N):
        if axis_iterator(i) in board:
            free -= 1

    return free


def clear_axes(
    board: dict[Coord, PlayerColor],
    row_range: list[int]=range(BOARD_N),
    col_range: list[int]=range(BOARD_N)
) -> None:
    """
    Acts in place - clears filled rows and columns on a game `board`. Only 
    checks for clearable axes in the row and column ranges supplied, to make 
    targetted clearing more efficient. Checks all rows and columns by default. 
    Returns nothing (None).
    """
    IRRELEVANT = 0

    # Find all cells that exist in checked filled rows/cols
    to_clear = set()
    for r in row_range:
        if free_cells(board, Coord(r,IRRELEVANT), "r") == 0:
            [to_clear.add(Coord(r,i)) for i in range(BOARD_N)]
    for c in col_range:
        if free_cells(board, Coord(IRRELEVANT,c), "c") == 0:
            [to_clear.add(Coord(i,c)) for i in range(BOARD_N)]

    # Drop these cells from board
    for tile in to_clear:
        board.pop(tile, 0)

    return None
    

def make_place(
    board: dict[Coord, PlayerColor], 
    place: PlaceAction, 
    color: PlayerColor,
) -> dict[Coord, PlayerColor]:
    """
    Assumes the place actions have been validated first, otherwise it can write
    over the top of existing cells. Places tetrominoes on a board, clearing rows
    / cols if filled. Acts in place - use with .copy() to generate new boards.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `PlayerColor` instances.  
        `place`: a `PlaceAction`instance of four coordinates of a tetromino
            piece to place onto the board.
        `color`: the core.py `PlayerColor` of the tetromino piece being played
    
    Returns:
        An altered board containing the changes of adding given tetromino piece
        and clearing now full axes.
    """
    placed_r = set()
    placed_c = set()

    for coord in place.coords:
        # Add coordinate axes to tracking sets then place token
        placed_r.add(coord.r)
        placed_c.add(coord.c)
        board[coord] = color

    # If necessary, clear now full rows and columns
    clear_axes(board, list(placed_r), list(placed_c))
    return board
