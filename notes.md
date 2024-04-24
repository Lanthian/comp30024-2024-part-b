# 2024.04.24
Cureent implementation breaks due to an illegal action taken - this seems to suggest that either game state isn't being
  tracked correctly, or move generation possible returns non-allowed moves. Need to look into.
* Rendered the board using utils.py - issue exists in move generation, not board state storing.
  * ACTUALLY, turns out the issue was that the PriorityDict that stored possible moves wasn't clearing between calls in 
    program.py action(). Implementing a simple .clear() method into prioritydict.py fixed this issue.