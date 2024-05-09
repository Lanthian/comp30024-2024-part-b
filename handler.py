"""handler.py: Runs the referee module and multiple different `Agent` class
implementations to handle testing and evaluation of strategies against each
other. Run with: 
    'python handler.py'
"""

__author__ = "Liam Anthian"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent
import subprocess
# import pandas as pd

from referee.game.constants import EXIT_CODE_WIN, EXIT_CODE_LOSE, EXIT_CODE_DRAW


class Agenthandler:
    """Class to store Agent implementation details and scoring from games."""
    path: str
    name: str
    score: dict[int: tuple[int,int,int]]

    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
 
        self.score = {}
        self.score[0] = (0,0,0)
        self.score[1] = (0,0,0)

    def __str__(self) -> str:
        return f"{self.name} @ {self.path}; R{self.score[0]} B{self.score[1]}"

    def update_score(self, player: int, outcome: int):
        """Adds a match outcome tuple to existing score count. `player` 
        represents starting turn of match for agent. `outcome` is a flag for 
        result from game match up - win, loss, or draw."""
        match outcome:
            case 1: x = (1,0,0)          # Win
            case 0: x = (0,1,0)          # Draw
            case -1: x = (0,0,1)         # Loss
        self.score[player] = add_tuple(self.score[player], x)


def main():
    RUNS = 5

    # Prepare agents
    agents = [Agenthandler("agent.a_rdm", "Rdm"),
              Agenthandler("agent.a_greedy", "Greedy"),
              Agenthandler("agent.a_grab", "Gr-αβ"),
              Agenthandler("agent.a_a-B", "α-β")]
    agent_selection = [agents[0], agents[2]]

    # Test agents (from both player 1 and player 2 perspectives)
    for red in agent_selection:
        for blu in agent_selection:

            # Command ran and stored RUNS amount of times
            cmd = ["python", "-m", "referee", red.path, blu.path]
            for i in range(RUNS):
                print(f"Running: {red.name} v {blu.name}, game {i+1}")
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL)

                # Interpret result
                u = interpret_returncode(result.returncode)
                if u == None: continue          # Error occured, skip

                red.update_score(0, u)
                blu.update_score(1, -u)

    # Stored data
    print([a.__str__() for a in agent_selection])


def simple_run(output: bool=True, count: int=1):
    """Basic function to manually play out a game without altering main()."""
    agent_1 = "agent.a_rdm"
    agent_2 = "agent.a_grab"
    command = ["python", "-m", "referee", agent_1, agent_2]
    # command = "python -m referee agent.a_rdm agent.a_greedy".split(" ")

    print("Running: " + " ".join(command))
    for i in range(count):
        if output: r = subprocess.run(command)
        else: r = subprocess.run(command, stdout=subprocess.DEVNULL)
        print(f"Outcome {i+1}: {interpret_returncode(r.returncode)}")


def interpret_returncode(returncode: int) -> int | None:
    """Shorthand function to interpret returncode from a referee subprocess
    depending on exit codes defined in referee.game.constants.py. Returns `None`
    if non game outcome specific returncode received."""
    if returncode           == EXIT_CODE_WIN: return 1
    elif returncode         == EXIT_CODE_LOSE: return -1
    elif returncode         == EXIT_CODE_DRAW: return 0
    else: return None


def add_tuple(a: tuple, b: tuple):
    """Returns the sum of two tuples `a` and `b` together. Will match the length
    of the shorter tuple."""
    def add(a,b):
        return a + b
    return tuple(map(add, a, b))


# main()
simple_run(True, 2)

# py handler.py
