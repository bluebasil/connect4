#####################################################
###              CODING CHALLENGE #1              ###
###                   Connect 4                   ###
###                                               ###
### Author: Elijah Moreau-Arnott                  ###
### Email:  elijahmad@gamil.com                   ###
###                                               ###
#####################################################

from errors import *
import copy



class Connect4:
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
        #determine legal moves
        #moves = {}
        max_move = 0
        max_score = -1
        for i in range(7):
            if grid[i][-1] == '':
                # i is a legal move
                move_score = self.dumb_play(self.execute_move(grid,self.mark,i),self.opposite_mark(self.mark), 0)
                print(move_score)
                if move_score > max_score:
                    move_score = max_score
                    max_move = i
        return max_move


    def dumb_play(self, grid, mark, depth):
        winner = self.check_win(grid)
        if winner == mark:
            print(f"Found a game where {mark} wins on turn {depth}")
            return 0
        if winner is not None:
            print(f"Found a game where {winner} wins on turn {depth}")
            return 1

        moves_found = 0
        sum_score = 0
        #max_score = -1
        for i in range(7):
            if grid[i][-1] == '':
                # i is a legal move
                sum_score += self.dumb_play(self.execute_move(grid,self.mark,i),self.opposite_mark(self.mark), depth + 1)
                #if sum_score > max_score:
                #    max_score = sum_score
                moves_found += 1
        if moves_found == 0:
            print(f"Found a game thats a draw on turn {depth}")
            return 0.1
        #return max_score
        return sum_score/moves_found

    def opposite_mark(self, mark):
        return 'r' if mark == 'y' else 'y'

    def check_win(self, grid):
        for column in grid:
            winner = self.check_line(column)
            if winner is not None:
                return winner

        for row_num in range(6):
            row = [column[row_num] for column in grid]
            winner = self.check_line(row)
            if winner is not None:
                return winner

        for diag_1 in range(3,10):
            column = min(diag_1, 6)
            line = []
            while column >= 0 and diag_1-column < 6:
                #print(f"Out of range {len(grid)} {column}, {len(grid[column])} {diag_1}")
                line.append(grid[column][diag_1-column])
                column -= 1
            winner = self.check_line(line)
            if winner is not None:
                return winner

        for diag_2 in range(3,10):
            column = min(diag_2, 6)
            line = []
            while column >= 0 and diag_2-column < 6:
                line.append(grid[6-column][diag_2-column])
                column -= 1
            winner = self.check_line(line)
            if winner is not None:
                return winner

        return None



    def check_line(self, line):
        for i in range(len(line)-3):
            winner = self.check_line_sebset(line[i:i+3])
            if winner is not None:
                return winner

    def check_line_sebset(self, cells):
        test_winner = cells[0]
        if test_winner == '':
            return None
        for c in cells:
            if c != test_winner:
                return None
        return test_winner

    def execute_move(self, grid, mark, move):
        spot = 0
        while grid[move][spot] != '':
            if spot == 6:
                print("tried to add to full column")
                self.print_grid(grid)
                exit()
                break
            spot += 1
        new_grid = copy.deepcopy(grid)
        new_grid[move][spot] = mark
        return new_grid

        
    def print_grid(self, grid):
        for col in grid:
            print(col)