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

# 2024.04.27
Some minor testing with new minimax implementation is needed, however too inefficient at the moment to even run depth 2. 
* Major changes to minimax structure, or some other form of alpha-beta pruning will be necessary to try reaching deeper
* Look into fixing structure to be faster, or only compute once number of possible moves is below some threshold (to
  minimise branching - an idea expressed by Anthony in Part A).
* Curious if a MCTS implementation can be done easily or not - might be the next thing to try


# 2024.04.30
* Alpha-Beta pruning minimax implemented - faster than default minimax for sure, but still struggles to function at 
  shallow turn counts with even weak depths (2 & 3). Need to write better heuristics to test it more.
* New ValWrap dataclass should be handy for storing moves and gamestates in different data structures.


# 2024.05.04
Issue with UCB1 seems to be a keyerror using MCTS.N[node], which makes me think that nodes are being regenerated in 
places and hashing different in the dictionary as a result. Removing this duplication of generation in all_children() 
method of a Node seems ot have fixed the problem.