# 2024.04.24
Current implementation breaks due to an illegal action taken - this seems to suggest that either game state isn't being
  tracked correctly, or move generation possible returns non-allowed moves. Need to look into.
* Rendered the board using utils.py - issue exists in move generation, not board state storing.
  * ACTUALLY, turns out the issue was that the PriorityDict that stored possible moves wasn't clearing between calls in 
    program.py action(). Implementing a simple .clear() method into prioritydict.py fixed this issue.



# 2024.04.26
Things we need to decide:
* How will we store game states (parent-children). Tree structure of some kind, but is each level sorted? New structure
  defined to handle alpha beta?
* What kinds of searches we want to code. Minimax? Monte Carlo?
* What heuristics we want to use to evaluate gamestates

### Heuristics:
* Value of a line clear (i.e. the ratio of blue:red tokens present in line cleared)
  * Potentially able to block line clears that would be negative to us by cutting off opponent's pieces
* Count of possible moves for the next player - maximising some ratio of blue:red moves possible (assuming we're red) 
  would be interesting
* Valuation of the fragmentation possible / present in a board state

Is there perhaps some easy way to generate hostile token structures?
* Shapes of our tokens that are dense (maximise end game value) but difficult to clear
* Building these near high density blue (opponent) zones reduces their placement options.

### agent_rdm
Messing around with competing agent against agent_rdm at the moment, I've come to the following notions:
* Even with such a basic heuristic, agent appears to ON AVERAGE outperform randomly selected moves. This might vary once
  any kind of non-hardcoded first move is introduced.
* Maybe just lucky/unlucky, but across testing it seems like the red player (first to move) wins more often than blue.
  * Hard to tell if this is from initial tile placement being red sided(?) or just a quirk of going first for this game.
