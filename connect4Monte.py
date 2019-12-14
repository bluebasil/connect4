import MonteCarlo
import copy
import math

class Connect4(MonteCarlo.Monte_Carlo):

    max_depth = 5

    def __init__(self, player_id):
        self.player_id = player_id

    def get_player_id(self):
        return  self.player_id

    def play(self, grid):
        ideal_move = self.get_ideal_move(grid, self.player_id, self.max_depth)
        return ideal_move

    def get_player_ids(self):
        return ['x', 'o']

    def get_next_player(self, player_id):
        next_player_id = self.get_player_ids()[self.get_player_ids().index(player_id)-1]
        return next_player_id

    def get_next_moveset(self, board, player_id):
        moveset = []
        for column_number in range(len(board)):
            if board[column_number][-1] == '':

                height = 0
                while board[column_number][height] != '':
                    height += 1

                resulting_board = copy.deepcopy(board)
                resulting_board[column_number][height] = player_id
                moveset.append((column_number, resulting_board))

        return moveset

    def get_score_table(self, board):
        #Check tie
        score_table = {}
        if self.check_tie(board):
            for player_id in self.get_player_ids():
                score_table[player_id] = None
            return score_table
        else:
            for player_id in self.get_player_ids():
                score_table[player_id] = 0

        for column in board:
            self.check_line_score(column, score_table)


        for row_num in range(6):
            row = [column[row_num] for column in board]
            self.check_line_score(row, score_table)

        for diag_1 in range(3, 9):
            column = min(diag_1, 6)
            line = []
            while column >= 0 and diag_1 - column < 6:
                # print(f"Out of range {len(grid)} {column}, {len(grid[column])} {diag_1}")
                line.append(board[column][diag_1 - column])
                column -= 1
            self.check_line_score(line, score_table)

        for diag_2 in range(3, 9):
            column = min(diag_2, 6)
            line = []
            while column >= 0 and diag_2 - column < 6:
                line.append(board[6 - column][diag_2 - column])
                column -= 1
            self.check_line_score(line, score_table)

        # make zero sum
        zero_sum_score_table = {}
        for key in score_table:
            final_score = 0
            for opponent_key in score_table:
                if key == opponent_key:
                    final_score += score_table[opponent_key]
                else:
                    final_score -= score_table[opponent_key]
            zero_sum_score_table[key] = final_score

        return zero_sum_score_table

    def check_tie(self, board):
        for column in board:
            if column[-1] == '':
                return False
        return True

    def check_line_score(self, line, score_table):
        line_score = 0
        for i in range(len(line) - 3):
            self.score_line_subset(line[i:i + 4], score_table)

    def score_line_subset(self, cells, score_table):
        contenders = {}

        for c in cells:
            if c in contenders:
                contenders[c] += 1
            else:
                contenders[c] = 1

        if len(contenders) == 1:
            if '' in contenders:
                # empty
                return 0
            # owned
            for key in contenders:
                score_table[key] = math.inf

        elif len(contenders) == 2 and '' in contenders:
            for key in contenders:
                if key != '':
                    score_table[key] += (contenders[key] ** 2)
