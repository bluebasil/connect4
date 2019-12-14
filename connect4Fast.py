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
import queue
from threading import Thread
import math
import time
from datetime import datetime, timedelta

#from multiprocessing import Process as Thread


class Connect4:
    """
    This is the class to handle all the games
    One instance per game
    You can save the state of the game or whatevere else you need in each instance of this class
    You can add as much code as you wish. Just keep the inital code given to you
    """
    DEBUG = False
    dif = 5
    
    def __init__(self, mark):
        """
        Initialize anything you will need
        
        :param mark: Player's mark for this game
        """
        
        self.mark = mark
        self.worst_score = -self.map_dir(mark)*math.inf
        self.calculations = {self.dif:{
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):4,
                        (('r', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):1,
                        (('y', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):1,
                        (('', '', '', '', '', ''), ('r', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):2,
                        (('', '', '', '', '', ''), ('y', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):2,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('r', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('y', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('r', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('y', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('r', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('y', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', '')):3,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('r', '', '', '', '', ''), ('', '', '', '', '', '')):4,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('y', '', '', '', '', ''), ('', '', '', '', '', '')):4, 
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('r', '', '', '', '', '')):5,
                        (('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('', '', '', '', '', ''), ('y', '', '', '', '', '')):5
                        }}
        self.last_move = None
        #self.workers = {3:None, 5:None, 7:None}
    
    def play(self, grid):
        """
        Will decide the best next move
        
        :param grid: The game's grid. 2D list of strings
        
        :return: The column to place your mark
        """
        timeout = datetime.now()
        
        self.check_for_errors(grid)
        self.trigger_calculation(grid, self.dif, 60)
        #self.trigger_calculation(grid, 3, 60)
        tuple_grid = self.convert(grid)


        while True:
            time.sleep(1)
            if self.get_best_move(tuple_grid) != None:
                break
            
            if (datetime.now()-timeout).total_seconds() > 54:
                if self.DEBUG:
                    print(f"breakout at time: {(datetime.now()-timeout).total_seconds()}s", flush=True)
                break


        ideal_move = self.get_move(tuple_grid, grid)
        new_grid = self.execute_move(grid, self.mark, ideal_move)
        self.last_move = new_grid
        #self.trigger_calculation(new_grid, 7, 120, opponents_turn=True)
        if self.DEBUG:
            print(f"turn end at time: {(datetime.now()-timeout).total_seconds()}s", flush=True)
        

        return ideal_move

    def get_player_id(self):
        return self.mark

    def check_for_errors(self, grid):
        if type(grid) is not list:
            raise InvalidInput("input should be a list")
        if len(grid) != 7:
            raise GridError("input should be a length 7 list of lists")
        for column in grid:
            if type(column) is not list:
                raise InvalidInput("input should be a list of lists")
            if len(column) != 6:
                raise GridError("input should be a list of length 6 lists")
            for cell in column:
                if not (cell == '' or cell == 'y' or cell == 'r'):
                    raise GridError(f"invalid cell with value {cell}.  cells should only have values 'r','y', or ''")
        if self.check_win(grid) is not None:
            raise GameIsOver()
        tuple_grid = self.convert(grid)
        if self.last_move is None and tuple_grid not in self.calculations[self.dif]:
            raise InvalidMove("game started with too many moves on the board")

        move_found = False
        for i in range(7):
            if grid[i][-1] == '':
                move_found = True
        if not move_found:
            raise GameIsOver("the board is full")

        if self.last_move is not None:
            potential_next_moves = set()
            for i in range(7):
                if self.last_move[i][-1] == '':
                    potential_move = self.execute_move(self.last_move,self.opposite_mark(self.mark),i)
                    potential_next_moves.add(self.convert(potential_move))
            if tuple_grid not in potential_next_moves:
                raise InvalidMove("game state not a natual progression since previous move")



    def convert(self, grid):
        columns = []
        for col in grid:
            columns.append(tuple(col))
        return tuple(columns)


    def get_best_move(self, tuple_grid):
        if tuple_grid in self.calculations[self.dif]:
            return self.calculations[self.dif][tuple_grid]
        return None

    def get_move(self, tuple_grid, grid):
        #for calc in (3):
        calc = self.dif
        if tuple_grid in self.calculations[calc]:
            if self.DEBUG:
                print(f"{self.mark} chosen calculation: {int((calc-1)/2)}/3", flush=True)
            return self.calculations[calc][tuple_grid]
        if self.DEBUG:
            print(f"{self.mark} ran out of time. chosen calculation random", flush=True)
        for i, c in enumerate(grid):
            if c[-1] == '':
                return i
        raise GameIsOver("The gameboard is full, game is over")

    
    def trigger_calculation(self,grid, depth, seconds, opponents_turn = False):
        # reset calcs
        time_limit = datetime.now() + timedelta(seconds=seconds)
        if opponents_turn:
            t = Thread(target=self.pre_empt_move, args=(grid, depth, time_limit))
            t.start()
        else:
            t = Thread(target=self.run_calculation, args=(grid, depth, time_limit))
            t.start()
        #self.workers[depth] = t

    def pre_empt_move(self, grid, depth, time_limit):

        for i in range(7):
            if grid[i][-1] == '':
                opponents_move = self.execute_move(grid,self.opposite_mark(self.mark),i)
                t = Thread(target=self.run_calculation, args=(opponents_move, depth, time_limit))
                t.start()

    def run_calculation(self,grid, depth, time_limit):
        #print(f"started calc {depth}", flush=True)
        ideal_move = 0
        ideal_score = self.worst_score

        que = queue.Queue()
        threads_list = list()

        for i in range(7):
            if grid[i][-1] == '':
                next_move = self.execute_move(grid,self.mark,i)
                t = Thread(target=lambda q, i, g, m, d, s, x, t: q.put((i,self.dumb_play(g,m,d,s,x, t))), args=(que, i, next_move,self.opposite_mark(self.mark), 0, self.worst_score, depth, time_limit))
                t.start()
                threads_list.append(t)

        for t in threads_list:
            t.join()

        if datetime.now() >= time_limit:
            #print(f"depth {depth} timeout", flush=True)
            return

        ideal_score = self.worst_score
        if self.mark == 'y':
            while not que.empty():
                score = que.get()
                #print(f"y -> {score[0]}: {score[1]}")
                if score[1] >= ideal_score:
                    ideal_score = score[1]
                    ideal_move = score[0]
        else:
            while not que.empty():
                score = que.get()
                #print(f"r -> {score[0]}: {score[1]}")
                if score[1] <= ideal_score:
                    ideal_score = score[1]
                    ideal_move = score[0]

        #print(f"DEPTH {depth}", flush = True)
        self.calculations[depth][self.convert(grid)] = ideal_move
        if self.DEBUG and depth == 3:
            print(f"{self.mark} prediction score: {ideal_move*self.map_dir(self.mark)}", flush=True)


    def dumb_play(self, grid, mark, depth, prune, max_depth, time_limit):
        #cur_score = self.check_score(grid)
        if depth == max_depth:
            return self.check_score(grid)


        winner = self.check_win(grid)
        if winner is not None:
            return -self.map_dir(mark)*math.inf

        moves_found = 0
        ideal_score = -self.map_dir(mark)*math.inf

        for i in range(7):
            if datetime.now() >= time_limit:
                return 0

            if grid[i][-1] == '':
                next_move = self.execute_move(grid,mark,i)

                score = self.dumb_play(next_move,self.opposite_mark(mark), depth + 1, ideal_score, max_depth, time_limit)
                if mark == 'r' and score < ideal_score:
                    ideal_score = score
                elif mark == 'y' and score > ideal_score:
                    ideal_score = score
                if mark == 'r' and score < prune:
                    return score
                elif mark == 'y' and score > prune:
                    return score

                moves_found += 1
        if moves_found == 0:
            return 0

        return ideal_score

    def opposite_mark(self, mark):
        return 'r' if mark == 'y' else 'y'

    def check_win(self, grid):
        """
        :return: None if there is no winner.  The winning mark if there is.
        """
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
            winner = self.check_line_sebset(line[i:i+4])
            if winner is not None:
                #print(f"winning line: {winner}")
                #print(line[i:i+4])
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
                # This should never happpen
                break
            spot += 1
        new_grid = copy.deepcopy(grid)
        new_grid[move][spot] = mark
        return new_grid

        
    def print_grid(self, grid):
        for col in grid:
            print(col)

    def map_dir(self,mark):
        if mark == 'y':
            return 1
        return -1

    def score_line_subset(self, cells):
        contenders = {}

        for c in cells:
            if c in contenders:
                contenders[c] += 1
            else:
                contenders[c] = 1

        if len(contenders) == 1:
            if '' in contenders:
                #empty
                return None
            #owned
            for key in contenders:
                return self.map_dir(key)*math.inf
        if len(contenders) == 2 and '' in contenders:
            for key in contenders:
                if key != '':
                    return self.map_dir(key)*(contenders[key]**2)
        return None

    def check_line_score(self, line):
        line_score = 0
        for i in range(len(line)-3):
            score = self.score_line_subset(line[i:i+4])
            if score is not None:
                line_score += score
        return line_score

    def check_score(self, grid):
        total_score = 0
        for column in grid:
            total_score += self.check_line_score(column)

        for row_num in range(6):
            row = [column[row_num] for column in grid]
            total_score += self.check_line_score(row)

        for diag_1 in range(3,10):
            column = min(diag_1, 6)
            line = []
            while column >= 0 and diag_1-column < 6:
                #print(f"Out of range {len(grid)} {column}, {len(grid[column])} {diag_1}")
                line.append(grid[column][diag_1-column])
                column -= 1
            total_score += self.check_line_score(line)

        for diag_2 in range(3,10):
            column = min(diag_2, 6)
            line = []
            while column >= 0 and diag_2-column < 6:
                line.append(grid[6-column][diag_2-column])
                column -= 1
            total_score += self.check_line_score(line)

        return total_score