"""handler.py: Runs the referee module and multiple different `Agent` class
implementations to handle testing and evaluation of strategies against each
other. Run with: 
    'python handler.py'
"""

__author__ = "Liam Anthian"
__credits__ = ["Liam Anthian", "Anthony Hill"] 

# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# === Imports ===
from datetime import datetime
import os
from re import sub
import subprocess

from referee.game.constants import EXIT_CODE_WIN, EXIT_CODE_LOSE, EXIT_CODE_DRAW


class Agenthandler:
    """Class to store Agent implementation details and scoring from games."""
    path: str
    name: str
    score: dict[str: dict[int: tuple[int,int,int]]]

    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self.score = {}

    def __str__(self) -> str:
        score_ratio = [f"{name}: R {self._ratio(s[0])}, B {self._ratio(s[1])}" 
                       for name,s in self.score.items()]
        return f"{self.name} @ {self.path}; {score_ratio}"

    def update_score(self, opp: str, player: int, outcome: int):
        """Adds a match outcome tuple to existing score count. `opponent` is the
        name of the agent versed. `player` represents starting turn of match for 
        agent. `outcome` is a flag for result from game match up - win, loss, or 
        draw."""
        # Register new opponent if not seen before
        if opp not in self.score:
            self.score[opp] = {}
            self.score[opp][0] = (0,0,0)        # Red
            self.score[opp][1] = (0,0,0)        # Blue

        match outcome:
            case 1: x = (1,0,0)          # Win
            case 0: x = (0,1,0)          # Draw
            case -1: x = (0,0,1)         # Loss
        self.score[opp][player] = add_tuple(self.score[opp][player], x)

    def _ratio(self, x: tuple[int,int,int]) -> str:
        """Converts a (win,draw,loss) three tuple into a win/loss string ratio.
        Doesn't calculate actual float value."""
        return f"{x[0]}/{x[2]}"


def main():
    RUNS = 1

    # Prepare agents
    agents = [Agenthandler("agent.a_rdm", "Rdm"),
              Agenthandler("agent.a_greedy", "Greedy"),
              Agenthandler("agent.a_grab", "Gr-aB"),
              Agenthandler("agent.a_a-B", "a-B"),
              Agenthandler("agnet.a_mcts", "MCTS")]
    agent_selection = agents[0:2] #agents[0:3]   #[agents[0], agents[1]]


    # Prepare backup output file
    """Below code inspired by stackoverflow post by user hetsch:
        Post: https://stackoverflow.com/a/14125914
        User: https://stackoverflow.com/users/1230358/hetsch"""
    file_name = f"{sub('[-.: ]', '', str(datetime.now()))}.txt"
    directory = os.path.join(os.getcwd(), r'out')
    # Make directory if non-existant
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Open the file!
    fp = open(os.path.join(directory, file_name), "w")


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

                red.update_score(blu.name, 0, u)
                blu.update_score(red.name, 1, -u)

                # Print to backup
                fp.write(f"Running: {red.name} v {blu.name}, game {i+1}" + 
                         " -- " +
                         f"Outcome: {interpret_returncode(result.returncode)}" +
                         "\n")

    # Output Stored data
    for a in agent_selection:
        print(a.__str__())
        fp.write(a.__str__() + "\n")
    # print([a.__str__() for a in agent_selection])

    # Close output file
    fp.close()


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


main()
# simple_run(True, 1)

# py handler.py
