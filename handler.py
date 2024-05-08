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

from referee.game import PlayerColor

def main():
    RUNS = 1

    # Prepare agents
    agents = [Agenthandler("agent.a_rdm", "Rdm")]
            #   Agenthandler("agent.a_greedy", "Greedy")]

    # Test agents
    for red in agents:
        for blu in agents:
            # Command ran
            cmd = ["python", "-m", "referee", red.path, blu.path]
            for _ in range(RUNS):
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL)
                print(result.stdout)
                red.update_score(0, 1)
                blu.update_score(1, 1*-1)

    print([a.__str__() for a in agents])


    # command = "python -m referee agent.a_rdm agent.a_greedy".split(" ")
    # result = subprocess.run(command)
    # print(result.stdout)

# python handler.py

# class Outcome:
#     code: int
#     outcome: tuple[int,int,int]

#     def __init__(self, code: int):
#         self.code = code
#         match code:
#             case 1: self.outcome = (1,0,0)          # Win
#             case 0: self.outcome = (0,1,0)          # Draw
#             case -1: self.outcome = (0,0,1)         # Loss

#     def __str__(self) -> str:
#         if self.code == 1:      return "Win"
#         elif self.code == -1:   return "Loss"
#         else:                   return "Draw"

#     def invert(self) -> 'Outcome':
#         return Outcome(self.code * -1)
    

class Agenthandler:
    path: str
    name: str
    
    score: dict[int: tuple[int,int,int]]
    # score: dict[PlayerColor: Outcome]
    # score_blu: tuple[int,int,int]

    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
 
        self.score = {}
        self.score[0] = (0,0,0)
        self.score[1] = (0,0,0)
        # self.score[PlayerColor.RED] = (0,0,0)
        # self.score[PlayerColor.BLUE] = (0,0,0)

    def __str__(self) -> str:
        return f"{self.name} @ {self.path}; R{self.score[0]} B{self.score[1]}"

    def update_score(self, color: int, outcome: int):
        match outcome:
            case 1: x = (1,0,0)          # Win
            case 0: x = (0,1,0)          # Draw
            case -1: x = (0,0,1)         # Loss
        self.score[color] = add_tuple(self.score[color], x)


def add_tuple(a: tuple, b: tuple):
    def add(a,b):
        return a + b
    return tuple(map(add, a, b))


# print(add_tuple((0,1,2,3), (0,1,2)))
main()
