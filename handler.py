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

command = "python -m referee agent.a_greedy agent.a_greedy".split(" ")
result = subprocess.run(command)
print("neat")
print(result.stdout)

# python handler.py
