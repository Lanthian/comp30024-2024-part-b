# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord

# python -m referee agent agent
BOARD_SIZE = 11  # size of board
class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """
    

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        
        self.color = color
        self.game_board = {}  # Dictionary to maintain the game state
        self.initialize_game_board()

    def initialize_game_board(self):
        """
        Initialize or reset the game board to an empty state.
        """
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.game_board[(r, c)] = None


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 

        Need to update this for action
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        match self.color:
            case PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                #nextMove = self.getNextMove(self.color)
                return PlaceAction(
                    Coord(5, 4), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                #nextMove = self.getNextMove(self.color)
                return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 

        note: this updates internal state (non-printed one) for further move calculation, game separately extracts board state 
        to print visually 
        """


        # There is only one action type, PlaceAction
        for coord in action.coords:
                self.game_board[(coord.r, coord.c)] = color

        c1, c2, c3, c4 = action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")

        