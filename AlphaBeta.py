import math
import copy
from threading import Thread
import queue

class Alpha_Beta:

    worst_score_table = None

    async_on = True

    def _try(self, board, player_id, depth, max_depth, prune_score):

        score_table = self.get_score_table(board)
        if depth == max_depth or list(score_table.values())[0] is None or math.isinf(list(score_table.values())[0]):
            return score_table

        maximize_score_table = copy.deepcopy(self.worst_score_table)
        maximize_score_table[self.get_next_player(player_id)] = math.inf

        for move_id, next_board_state in self.get_next_moveset(board, player_id):
            score_table = self._try(next_board_state, self.get_next_player(player_id), depth + 1, max_depth, maximize_score_table)
            if score_table[player_id] > prune_score[player_id]:
                return score_table
            if score_table[player_id] >= maximize_score_table[player_id]:
                maximize_score_table = score_table

        return maximize_score_table



    def get_ideal_move(self, board, player_id, max_depth):
        # will return a move_id

        self.worst_score_table = {}
        for pid in self.get_player_ids():
            self.worst_score_table[pid] = -math.inf

        initial_prune = copy.deepcopy(self.worst_score_table)
        initial_prune[self.get_next_player(player_id)] = math.inf

        moves = self.get_next_moveset(board, player_id)
        que = queue.Queue()
        threads_list = list()

        ideal_move = None
        for mode_id, next_board_state in self.get_next_moveset(board, player_id):
            if self.async_on:
                t = Thread(target=lambda q, i, b, pid, d, md, p: q.put((i, self._try(b, pid, d, md, p))),
                           args=(que, mode_id, next_board_state, self.get_next_player(player_id), 0, max_depth, initial_prune))
                t.start()
                threads_list.append(t)
            else:
                que.put((mode_id, self._try(next_board_state, self.get_next_player(player_id), 0, max_depth, initial_prune)))
            ideal_move = mode_id

        for t in threads_list:
            t.join()

        maximize_score_table = self.worst_score_table
        while not que.empty():
            score_mapping = que.get()
            #print(score_mapping[0], score_mapping[1][player_id])
            if score_mapping[1][player_id] >= maximize_score_table[player_id]:
                maximize_score_table = score_mapping[1]
                ideal_move = score_mapping[0]

        return ideal_move

    def get_score_table(self, board):
        # win should return math.inf, lose should return -math.inf, game otherwise over should return None
        raise NotImplementedError
        #return {'r': math.inf, 'y': -math.inf}

    def get_next_moveset(self, board, player_id):
        # list of move_id - board outcome tuples
        raise NotImplementedError
        #return [(0,board)]

    def get_next_player(self, current_player_id):
        # list of move_id - board outcome tuples
        raise NotImplementedError
        # return not current_player_id

    def get_player_ids(self):
        raise NotImplementedError
        #return ['r','y']