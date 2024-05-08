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

# 2024.05.05
* I've spent too much timing messing around with MCTS as it is - rather than beating my head against a brick wall, a new 
  approach would be good. We should try to have it so the tree can be trained from any node, and next move requested 
  from any node.
* Problem mostly solved (experimental branch - divide by zero error is not terrific...) however it's absolutely 
  horrendous for memory.

### Progress update (LA)
A quick update of where we’re at (I think); I’ve been messing around with mcts and it’s pretty terrible early game, and 
can be really really memory intensive. If we were to use it we should train up a prestored dictionary of planned moves 
for different scenarios early game, or use a-B search and then segue into mcts once mid game or late game.
It’s also reached the point where fiddling with it / improving it further is too time intensive for me for the time we 
have left, so I’m going to instead get on with starting the report and polishing a-B for submission. If you’d like to 
give MCTS a crack I more than welcome it, or if you want to direct efforts elsewhere that’s also fine. I like the idea 
of monte carlo but just struggling a bit too much with the limited time I have in the coming week to complete it.


# 2024.05.07
Noting down a quick idea before I forget it -- the slowest part of the program right now (besides branching factor of
  looking deeper) is the generation of children states from this branching factor. If we instead store pre-computed
  children rather than regenerating them, we can trade memory for processing time. If managed correctly we shouldn't
  overflow memory limitations, and should hopefully speed up processing time majorly.
* Today I've also restructured the directory to make coding alternative bots easier

# 2024.05.08
In the process of separating the agents into their own folders, many MANY previously unnoticed bugs have been fixed.
Some examples include:
* Non ValWrapped tuples in minimax
* Missing terminal check for turn count > 150 in a-B and minimax
* Redundant TURN_CAP given MAX_TURNS in referee.game.constants
* Turn count in Gamestate not copied over when using .copy() method of class
Additionally, a lot of comments and documentation have been altered + added, and large commented out junks of code 
deleted.

# 2024.05.09
* Testing with a-B changed to store generated possible_moves found that across multiple games up to and above turn 35,
  no stored moves were ever retrieved (that is, no use was found from this storing process).
  * I've opted to remove the code that stored these states in turn for the time being, but it can always be added back
    if another idea is found that wishes to encorporate them.
    ``` 
    seen: dict[str: list[Action]]

    # Avoid recalculating possible moves by storing game state in `seen`
    flat_b = flatten_board(game.board)
    if flat_b not in agt.seen: 
        agt.seen[flat_b] = possible_moves(game.board, game.current)
    next_moves = agt.seen[flat_b]
    ```