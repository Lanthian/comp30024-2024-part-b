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

from referee.game.constants import EXIT_CODE_WIN, EXIT_CODE_LOSE, EXIT_CODE_DRAW

def main():
    RUNS = 5

    # Prepare agents
    agents = [Agenthandler("agent.a_rdm", "Rdm"),
              Agenthandler("agent.a_greedy", "Greedy"),
              Agenthandler("agent.a_a-B", "α-β")]

    # Test agents (from both player 1 and player 2 perspectives)
    for red in agents:
        for blu in agents:

            # Command ran and stored RUNS amount of times
            cmd = ["python", "-m", "referee", red.path, blu.path]
            for i in range(RUNS):
                print(f"Running: {red.name} v {blu.name}, game {i+1}")
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL)

                # Interpret result
                if result.returncode    == EXIT_CODE_WIN: u = 1
                elif result.returncode  == EXIT_CODE_LOSE: u = -1
                elif result.returncode  == EXIT_CODE_DRAW: u = 0
                else: continue          # Error occured, skip

                red.update_score(0, u)
                blu.update_score(1, -u)

    # Stored data
    print([a.__str__() for a in agents])


def simple_run():
    """Basic function to manually play out a game without altering main()."""
    agent_1 = "agent.a_rdm"
    agent_2 = "agent.a_greedy"
    command = ["python", "-m", "referee", agent_1, agent_2]
    # command = "python -m referee agent.a_rdm agent.a_greedy".split(" ")
    subprocess.run(command)


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


def add_tuple(a: tuple, b: tuple):
    """Returns the sum of two tuples `a` and `b` together. Will match the length
    of the shorter tuple."""
    def add(a,b):
        return a + b
    return tuple(map(add, a, b))


main()
# simple_run()

# python handler.py
