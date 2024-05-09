"""heuristics.py: Measures for Tetress Gamestates to evaluate how positive or 
negative a current board state is for a given player. All functions return 
numbers (ints or floats)."""

__author__ = "Liam Anthian"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from numbers import Number

from agent.control import possible_moves
from agent.gamestate import Gamestate
from referee.game import Coord, Direction, PlayerColor


def h1(game: Gamestate, color: PlayerColor) -> int:
    """Returns the integer token count difference between opponent and player 
    `color` in a Gamestate `game`. A larger number is better for player.
    Goal: Maximise difference in player tiles on board."""
    # Note - tends to maximise I piece placements when paired with h3
    return game.counts[color] - game.counts[color.opponent]

def h2(game: Gamestate, color: PlayerColor) -> int:
    """Returns the interger possible move difference between opponent and player
    `color` in a Gamestate `game`. A larger number is better for player.
    Goal: Maximise difference in remaining possible moves between players."""
    # Note - Not feasible to calculate with higher branching factor (move count) 
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

def multi_h(hs: list[tuple], game: Gamestate, color: PlayerColor) -> Number:
    """Shorthand to evaluate multiple heuristic functions across game data. `hs`
    is a list of tupled heuristics (e.g. h1, h3) and their weightings, `game` is
    the Gamestate upon which calculation will be performed, and `color` is the 
    perspective from which this heuristic evaluation will be viewed.
    Returns a Number (int/float)."""
    return sum([h(game,color)*w for (h,w) in hs])

def h_combiner(hs: list[tuple['function',float]]) -> 'function':
    """Shorthand to produce a combined evaluator of multiple heuristics. `hs`
    is a list of tupled heuristics (e.g. h1, h3) and their weightings. Returns
    a function which converts a Gamestate `game` and player perspective `color`
    to a heuristic number."""
    return lambda game, color: sum([h(game,color)*w for (h,w) in hs])
