from errors import *


class Connect4Manual:
    """
    This is the class to handle all the games
    One instance per game
    You can save the state of the game or whatevere else you need in each instance of this class
    You can add as much code as you wish. Just keep the inital code given to you
    """
    
    def __init__(self, mark):
        """
        Initialize anything you will need
        
        :param mark: Player's mark for this game
        """
        
        self.mark = mark
    
    
    def play(self, grid):
        """
        Will decide the best next move
        
        :param grid: The game's grid. 2D list of strings
        
        :return: The column to place your mark
        """
        self.print_grid(grid)
        move = -1
        try:
            move_str = input("Choose a column: ")
            move = int(move_str)
        except:
            print("Invalid number")
            return self.play(grid)
        if move < 0 or move > 6:
            print("not a column")
            return self.play(grid)
        return move

    def print_grid(self, grid):
        for col in grid:
            print(col)