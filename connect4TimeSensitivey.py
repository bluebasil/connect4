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
#import threading
import ctypes
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
    
    def __init__(self, mark):
        """
        Initialize anything you will need
        
        :param mark: Player's mark for this game
        """
        
        self.mark = mark
        self.worst_score = -self.map_dir(mark)*math.inf
        self.calculations = {3:None, 4:None, 5:None, 6:None, 7:None}
        #self.workers = {3:None, 5:None, 7:None}
    
    def play(self, grid):
        print(self.convert(grid))
        """
        Will decide the best next move
        
        :param grid: The game's grid. 2D list of strings
        
        :return: The column to place your mark
        """
        self.trigger_calculation(grid, 7, 1000)
        self.trigger_calculation(grid, 6, 500)
        self.trigger_calculation(grid, 5, 60)
        self.trigger_calculation(grid, 4, 60)
        self.trigger_calculation(grid, 3, 60)


        #time.sleep(2)
        #self.trigger_calculation(grid,7)
        for time_passed in range(0,1000,5):
            time.sleep(5)
            print(time_passed, self.calculations, flush=True)
            if self.get_best_move() != None:
                return self.get_best_move()
        time.sleep(3)
        ideal_move = self.get_move(grid)

        #self.trigger_calculation(grid, 7, 120)
        #self.trigger_calculation(grid, 5, 60)
        #self.trigger_calculation(grid, 3, 60)

        return ideal_move

    def convert(self, grid):
        columns = []
        for col in grid:
            columns.append(tuple(col))
        return tuple(columns)


    def get_best_move(self):
        return self.calculations[7]

    def get_move(self, grid):
        for calc in (7,5,3):
            if self.calculations[calc] != None:
                print(f"choose {calc}", flush=True)
                return self.calculations[calc]
        print("random move", flush=True)
        for i, c in enumerate(grid):
            if c[-1] == '':
                return i
        raise GameIsOver("The gameboard is full, game is over.")

    
    def trigger_calculation(self,grid, depth, seconds):
        # reset calcs
        self.calculations[depth] = None
        time_limit = datetime.now() + timedelta(seconds=seconds)
        t = Thread(target=self.run_calculation, args=(grid, depth, time_limit))
        #print(t.get_id())
        t.start()
        #self.workers[depth] = t

    def run_calculation(self,grid, depth, time_limit):
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
            print(f"depth {depth} timeout", flush=True)
            return

        ideal_score = self.worst_score
        if self.mark == 'y':
            while not que.empty():
                score = que.get()
                print(f"y -> {score[0]}: {score[1]}")
                if score[1] >= ideal_score:
                    ideal_score = score[1]
                    ideal_move = score[0]
        else:
            while not que.empty():
                score = que.get()
                print(f"r -> {score[0]}: {score[1]}")
                if score[1] <= ideal_score:
                    ideal_score = score[1]
                    ideal_move = score[0]

        self.calculations[depth] = ideal_move


    def dumb_play(self, grid, mark, depth, prune, max_depth, time_limit):
        try:
            #cur_score = self.check_score(grid)
            if depth == max_depth:
                return self.check_score(grid)


            winner = self.check_win(grid)
            if winner is not None:
                #self.print_grid(grid)
                #print(f"Found a game where {winner} wins on turn {depth} - I'm {mark}")
                return -self.map_dir(mark)*math.inf

            moves_found = 0
            #sum_score = 0
            ideal_score = -self.map_dir(mark)*math.inf
            #que = queue.Queue()
            #threads_list = list()
            for i in range(7):
                if datetime.now() >= time_limit:
                    print("mid timeout", flush=True)
                    return 0

                if grid[i][-1] == '':
                    next_move = self.execute_move(grid,mark,i)
                    #self.print_grid(next_move)
                    #print("###")

                    ###
                    # Threading
                    #t = Thread(target=lambda q, g, m, d: q.put(self.dumb_play(g,m,d)), args=(que, next_move,self.opposite_mark(mark), depth + 1))
                    #t.start()
                    #threads_list.append(t)
                    ###

                    ###
                    # No Threading
                    score = self.dumb_play(next_move,self.opposite_mark(mark), depth + 1, ideal_score, max_depth, time_limit)
                    if mark == 'r' and score < ideal_score:
                        ideal_score = score
                    elif mark == 'y' and score > ideal_score:
                        ideal_score = score
                    if mark == 'r' and score < prune:
                        return score
                    elif mark == 'y' and score > prune:
                        return score
                    #que.put(score)
                    ###

                    moves_found += 1
            if moves_found == 0:
                #self.print_grid(grid)
                print(f"Found a game thats a draw on turn {depth}", flush=True)
                return 0
            #for t in threads_list:
            #    t.join()

            #ideal_score = 0
            #if mark == 'y':
            #    ideal_score = -math.inf
            #    while not que.empty():
            #        score = que.get()
            #        if score > ideal_score:
            #            ideal_score = score
            #else:
            #    ideal_score = math.inf
            #    while not que.empty():
            #        score = que.get()
            #        if score < ideal_score:
            #            ideal_score = score
            #return max_score
            return ideal_score
        except HaltError:
            print("Child halted")
            return None

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