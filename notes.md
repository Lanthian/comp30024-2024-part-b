# 2024.04.24
Current implementation breaks due to an illegal action taken - this seems to suggest that either game state isn't being
  tracked correctly, or move generation possible returns non-allowed moves. Need to look into.
* Rendered the board using utils.py - issue exists in move generation, not board state storing.
  * ACTUALLY, turns out the issue was that the PriorityDict that stored possible moves wasn't clearing between calls in 
    program.py action(). Implementing a simple .clear() method into prioritydict.py fixed this issue.
  * 2024.05.09: Unsure if I noted it elsewhere, but this issue was also resolved by moving default values for the 
    PriorityDict class into an `__init__` function, instead of having it constant between all dictionaries....


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
(Early AMs):
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
* New a_greedy_a-B tested: Plays as a standard greedy Agent until < 15 possible moves remain, then it a-B searches 3
  moves ahead (new record high!). Can do 5 when given a decent amount of time, can do 4 reasonably but slowly.

(Morning):
* Code that stored states reintroduced, as with tests it's actually useful for depths > 2 (or 3) in
  a-B; depths that weren't used in a-B by itself but ARE used in Greedy_a-B. Whether or not it adds more processing than
  it saves, hard to say at the moment.

(Evening):
* Killer heuristic implementation attempted in Greedy_a-B, program timed out, meaning it surpassed 180 seconds for just
  one turn. Sorting possible_moves inside a-B is not a viable method of creating a killer heuristic unfortunately, as 
  this sorting step simply takes too long. Code will be archived here.
  ```
  # ATTEMPT AT KILLER HEURISTIC - sort moves before recursing over
  agt.seen[flat_b] = sorted_moves(game, game.current, h3)

  ...

  def sorted_moves(game: Gamestate, player: PlayerColor, heu) -> list[Action]:
    """
    Takes a Gamestate `game` and a `player` defined by their PlayerColor and 
    returns all possible next moves for said player in the form of a list of 
    Actions, SORTED according to value output by evaluator `heu`.
    """
    # Store moves in sets based on heuristic value
    mvs: dict[int: set] = {}

    for (coord, color) in game.board.items():
        if color == player:
            # duplicate moves generated and ignored here (possible improvement)
            for move in tetrominoes_plus(coord, set(game.board.keys())):
                # Generate child and evaluate according to `heu`
                h = heu(game.child(move, player), player)

                # Prepare set for new heuristic value `h` seen, then add on
                if h not in mvs: mvs[h] = set()
                mvs[h].add(move) 
    
    # Sort heuristic values (previous h's) ascending
    # print(mvs)

    heus = list(mvs.keys())
    heus.sort()       

    list_of_lists = [list(mvs[h]) for h in heus]
    flat = [j for i in list_of_lists for j in i]

    return flat
  ```  
* It seems that the main thing slowing down MCTS, a-B and all other searches is the expensiveness (time wise) to 
  generate all children states for a node. These endeavours today have shown that while attempting to optimise elsewhere
  isn't bad, the source of all problem at the moment is the stacking branching factor as we go down a path.
* Can try generating just one child node at a time for MCTS - should MASSIVELY improve the algorithm, but would require
  an unbiased method of generating 1/180 children states. Calling a function that is suspended and unpauses, calculates 
  and re-pauses whenever a new child is needed would be ideal. Any further work with MCTS should look into this.
