"""control.py: Provides functions to update and measure possible moves and 
qualities of a board state. Code imported from Part A of Tetress Project."""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlaceAction, PlayerColor, BOARD_N
from .tetrominoes import tetrominoes_plus
import random

def is_I_shape(action: PlaceAction) -> bool:
    """ Check if the given PlaceAction corresponds to an 'I' shape. """
    x_vals = [coord.c for coord in action.coords]
    y_vals = [coord.r for coord in action.coords]
    return len(set(x_vals)) == 1 or len(set(y_vals)) == 1

def is_adjacent(coord, board_keys):
    """Check if the coordinate is adjacent to any placed coord in the board, within valid bounds."""
    x, y = coord.c, coord.r
    # Define valid moves within the board boundaries
    possible_moves = [
        (nx, ny) for nx, ny in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        if 0 <= nx < BOARD_N and 0 <= ny < BOARD_N
    ]
    return any(Coord(nx, ny) in board_keys for nx, ny in possible_moves)

def count_adjacent(coords, board_keys):
    """Count how many coordinates are adjacent to existing pieces."""
    return sum(is_adjacent(coord, board_keys) for coord in coords)

def first_move(board: dict):
    """
    Takes a game `board` and returns a random PlaceAction on the board depending on whether its first move or second move (any colour can start)
    """
    if len(board) == 0:
        random_coord = Coord(random.randint(0, BOARD_N - 1), random.randint(0, BOARD_N - 1))
        possible_actions = tetrominoes_plus(random_coord, set(board.keys())) # empty board, arbitrary location as there are infinite edges meaning no strategic benefit of location
        non_I_actions = [action for action in possible_actions if not is_I_shape(action)] #  shape is not straight to limit risk in one axes
        return random.choice(non_I_actions)
    else:
        occupied_coords = list(board.keys())
        possible_actions = tetrominoes_plus(random.choice(occupied_coords), set(board.keys()))
        non_I_actions = [action for action in possible_actions if not is_I_shape(action)] #  shape is not straight to limit risk in one axes
        return random.choice(non_I_actions)
        """ to be worked on, makes it so that 2nd move has 2 adjacent coords 
        board_keys = set(board.keys())
        occupied_coords = list(board.keys())
        possible_actions = tetrominoes_plus(random.choice(occupied_coords), set(board.keys()))
        valid_actions = [action for action in possible_actions if count_adjacent(action.coords, board_keys) >= 2]
        return random.choice(valid_actions)
        """
    
    
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
