import math
import copy
from threading import Thread
import queue
import random
from datetime import datetime, timedelta

class Monte_Carlo:

    worst_score_table = None

    async_on = True

    node_catalogue = {}

    time_limit = 5

    class monteNode:
        def __init__(self):
            self.children = []
            self.simulation_count = 0
            self.win_stats = {}
            self.board_state = None
            self.move_id = -1
            self.owner = 'y'
            self.leaf_node = False
            self.winner = None

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

            self.node_catalogue[self.get_board_string(next_board_state)] = new_child
            node.children.append(new_child)

    def create_root_node(self, board, owner):

        new_node = self.monteNode()
        new_node.board_state = board
        new_node.owner = owner
        empty_stats = {}
        for pid in self.get_player_ids():
            empty_stats[pid] = 0
        new_node.win_stats = empty_stats

        self.node_catalogue[self.get_board_string(board)] = new_node
        return new_node




    def _simulate(self, node):
        #print(node.board_state)
        if node.leaf_node:
            self._apply_simulation(node,node.winner)
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
                self._apply_simulation(node,winner_id)

            return node.win_stats, node.simulation_count

    def _playout(self, node, parent_owner):
        score_table = self.get_score_table(node.board_state)
        for player_id in score_table:

            if score_table[player_id] is None:
                node.leaf_node = True
                node.winner = None
                self._apply_simulation(node,player_id)
                return None

            if math.isinf(score_table[player_id]) and score_table[player_id] > 0:
                node.leaf_node = True
                node.winner = player_id
                self._apply_simulation(node,player_id)
                return player_id

        winner_id = self._deep_playout(node.board_state, node.owner)
        self._apply_simulation(node,winner_id)
        return winner_id



    def _apply_simulation(self, node, winner_id):
        node.simulation_count += 1
        if winner_id is None:
            for pid in node.win_stats:
                node.win_stats[pid] += 0.5
        else:
            node.win_stats[winner_id] += 1


    def _deep_playout(self, board, player_id):
        score_table = self.get_score_table(board)
        for pid in score_table:
            if score_table[pid] is None:
                return None
            if math.isinf(score_table[pid]) and score_table[pid] > 0:
                #print(f"{pid} WON:")
                #self.print_grid(board)
                return pid

        moves_choice = self.get_next_moveset(board, player_id)
        chosen = random.choice(moves_choice)
        return self._deep_playout(chosen[1], self.get_next_player(player_id))

    # def print_grid(self, grid):
    #
    #     # for col in grid:
    #     #    print(col)
    #     print("---------")
    #     for row_num in range(5, -1, -1):
    #         row = [column[row_num] for column in grid]
    #         print("|", end='')
    #         for c in row:
    #             s = " "
    #             if c == 'o':
    #                 # sys.stdout.buffer.write(TestText2)
    #                 s = 'O'
    #                 # s = b'●'
    #             elif c == 'x':
    #                 # sys.stdout.buffer.write(TestText2)
    #                 s = 'X'
    #                 # s = b'○'
    #             print(s, end='')
    #         print("|")
    #     print("|0123456|", flush=True)

    def get_ideal_move(self, board, player_id, max_depth):
        # will return a move_id
        root_node = None
        # if self.get_board_string(board) in self.node_catalogue:
        #     root_node = self.node_catalogue[self.get_board_string(board)]
        # else:
        root_node = self.create_root_node(board, player_id)
        #
        # timeout = datetime.now()
        # while (datetime.now()-timeout).total_seconds() < self.time_limit:
        #     self._simulate(root_node)

        for i in range(21):
            self._simulate(root_node)

        most_sims = -1
        ideal_move = -1
        max_wins = -1
        for child_node in root_node.children:
            if child_node.simulation_count > most_sims:
                ideal_move = child_node.move_id
                most_sims = child_node.simulation_count
                max_wins = child_node.win_stats[player_id]
            if child_node.simulation_count == most_sims and child_node.win_stats[player_id] > max_wins:
                ideal_move = child_node.move_id
                max_wins = child_node.win_stats[player_id]

        self._print_tree(root_node)
        return ideal_move


    def _print_tree(self, root, width=1000):
        level = [root]
        while len(level) > 0:
            self._print_level(level, width)
            next_level = []
            for node in level:
                #if len(node.children) > 0:
                next_level.extend(node.children)
                #else:
                #    next_level.extend(['']*7)
            level = next_level


    def _node_string(self, node):
        return f"{node.win_stats[self.get_player_ids()[0]]}/{node.simulation_count}"

    def _print_level(self, level, width):
        spacing = int(width/len(level))
        for node in level:
            print(f"{self._node_string(node):^{spacing}}", end='')
        print()



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

    def get_board_string(self, board):
        raise NotImplementedError