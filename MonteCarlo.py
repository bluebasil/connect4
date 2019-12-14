import math
import copy
from threading import Thread
import queue
import random

class Monte_Carlo:

    worst_score_table = None

    async_on = False

    class monteNode:
        def __init__(self):
            self.children = []
            self.simulation_count = 0
            self.win_stats = {}
            self.board_state = None
            self.move_id = -1
            self.owner = 'y'
            self.leaf_node = False

    def create_monte_child(self, node):
        for move_id, next_board_state in self.get_next_moveset(node.board_state, node.owner):
            new_child = self.monteNode()
            new_child.board_state = next_board_state
            new_child.move_id = move_id
            new_child.owner = self.get_next_player(node.owner)
            empty_stats = {}
            for pid in self.get_player_ids():
                empty_stats[pid] = 0
            new_child.win_stats = empty_stats
            node.children.append(new_child)

    def create_root_node(self, board, owner):
        new_node = self.monteNode()
        new_node.board_state = board
        new_node.owner = owner
        empty_stats = {}
        for pid in self.get_player_ids():
            empty_stats[pid] = 0
        new_node.win_stats = empty_stats
        return new_node


    def _simulate(self, node):
        #print(node.board_state)
        if node.leaf_node:
            return node.win_stats, node.simulation_count

        if len(node.children) != 0:
            best_child = None
            best_score = -math.inf
            for child in node.children:
                n = child.simulation_count

                if n > 0:
                    w = child.win_stats[node.owner]
                    N = node.simulation_count + 1
                    c = math.sqrt(2)
                    score = w/n + c*math.sqrt(math.log(N, math.e)/n)
                    if score >= best_score:
                        best_score = score
                        best_child = child
                else:
                    # we found a leaf node
                    best_child = child
                    break

            winner_stats, sims = self._simulate(best_child)
            for winner_id in winner_stats:
                node.win_stats[winner_id] += winner_stats[winner_id]
            node.simulation_count += sims
            return winner_stats, node.simulation_count
        else:
            # leaf node reached: playout
            self.create_monte_child(node)
            que = queue.Queue()
            threads_list = list()

            for child_node in node.children:
                if self.async_on:
                    t = Thread(target=lambda q, n, o: q.put(self._playout(n, o)),
                               args=(que, child_node, node.owner))
                    t.start()
                    threads_list.append(t)
                else:
                    que.put(self._playout(child_node, node.owner))

            for t in threads_list:
                t.join()

            winner_stats = {}
            for player_id in self.get_player_ids():
                winner_stats[player_id] = 0
            while not que.empty():
                winner_id = que.get()
                if winner_id is not None:
                    winner_stats[winner_id] += 1

                else:
                    # Tie
                    for player_id in self.get_player_ids():
                        winner_stats[player_id] += 0.5

            node.win_stats = winner_stats
            node.simulation_count = len(node.children)
            return node.win_stats, node.simulation_count

    def _playout(self, node, parent_owner):
        node.simulation_count += 1

        score_table = self.get_score_table(node.board_state)
        for player_id in score_table:

            if score_table[player_id] is None:
                node.leaf_node = True
                for player_id in node.win_stats:
                    node.win_stats[player_id] = 0.5
                return None

            if math.isinf(score_table[player_id]) and score_table[player_id] > 0:
                node.leaf_node = True
                node.win_stats[player_id] += 1
                return parent_owner

        return self._deep_playout(node.board_state, node.owner)

    def _deep_playout(self, board, player_id):
        score_table = self.get_score_table(board)
        for pid in score_table:
            if score_table[pid] is None:
                return None
            if math.isinf(score_table[pid]) and score_table[pid] > 0:
                return pid

        moves_choice = self.get_next_moveset(board, player_id)
        chosen = random.choice(moves_choice)
        return self._deep_playout(chosen[1], self.get_next_player(player_id))

    def get_ideal_move(self, board, player_id, max_depth):
        # will return a move_id

        root_node = self.create_root_node(board, player_id)
        for i in range(50):
            self._simulate(root_node)

        most_sims = -1
        ideal_move = -1
        for child_node in root_node.children:
            if child_node.simulation_count > most_sims:
                ideal_move = child_node.move_id
                most_sims = child_node.simulation_count


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