"""tetrominoes.py: Provides functions to generate lists of 4 Coord PlaceActions
based on the dataclasses present in core.py"""

__author__ = "Liam Anthian, and Anthony Hill"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, Direction, PlaceAction

def tetrominoes(
        c: Coord,
        tiles: set[Coord]=set()
) -> list[PlaceAction]:
    """Takes a Coord c and generates a list of Place actions of all unique 4 
    tiled "tetrominoes" that include this coordinate, relating to the board size
    defined in core.py. List should be of length 76 if `tiles` is empty.
    (z*2 + s*2 + i*2 + t*4 + o*1 + j*4 + l*4) * 4 = 19 * 4 = 76

    Parameters:
        `c`: a Coord on which place actions should be centred around (including)
        `tiles`: set of Coords which should not be included in any place 
            actions and will limit the size of the output - empty by default 
    
    Returns:
        A list of lists of Coords (list of place actions) or in the case that 
            starting coordinate is present in `avoid_coord` list, and empty list
    """
    t = []

    # Safety check if no possible tetrominos to generate from starting coord
    if c in tiles: return t

    in_progress = [[c]]
    seen = []               
    # Work through a queue of semi-assembled tetrominoes to build whole set
    while len(in_progress) > 0:
        curr = in_progress.pop(0)
        curr.sort()     # ensures each piece+place is always defined the same
        # Skip node if already seen
        if curr in seen:
            continue

        # otherwise, add to seen set and check if valid
        else:
            seen.append(curr)
            if len(curr) == 4:
                # valid tetromino - convert to PlaceAction
                t.append(PlaceAction(curr[0],curr[1],curr[2],curr[3]))
                continue
        
        # Loop through each direction for each piece, attaching a new block
        for coord in curr:
            for dir in [d.value for d in Direction]:
                new = Coord.__add__(coord, dir)
                # Avoid duplicating existing and including disallowed coords
                if (new in curr) or (new in tiles): continue
                in_progress.append(curr + [new])

    return t


def tetrominoes_plus(
    c: Coord,
    tiles: set[Coord]=set()
) -> list[PlaceAction]:
    """Takes a Coord c and generates a list of Place actions of all unique 4 
    tiled "tetrominoes" that build off of this coordinate, that is, are adjacent
    to the coordinate but do NOT include it. Additionally, can take a set
    (empty by default) to check if neighbouring cells are already filled and 
    shorten calculation.
    """
    t = []

    # Disinclude middle coord to form pattern
    if c not in tiles: tiles.add(c)

    for dir in [d.value for d in Direction]:
        new = Coord.__add__(c, dir)

        # Add surrounding tetrominoes, omitting centre tile, and dropping dups
        t += ([t1 for t1 in tetrominoes(new, tiles) if t1 not in t])
        # (1*s, 1*z, 1*l, 1*j, 2*t) * 4 = 24 dropped as dup (if `tiles` empty)

    return t
