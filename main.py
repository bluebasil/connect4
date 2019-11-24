from connect4 import *
from player import *
from copy import deepcopy

players = []
#players.append(Connect4Manual('y'))
#players.append(Connect4Manual('r'))
players.append(Connect4('r'))
players.append(Connect4Manual('y'))

grid = []
for i in range(7):
    column = []
    for j in range(6):
        column.append('')
    grid.append(column)

while True:
    for p in players:
        temp_grid = deepcopy(grid)
        move = p.play(temp_grid)
        spot = 0
        while grid[move][spot] != '':
            if spot == 5:
                print("tried to add to full column")
                print(grid)
                exit()
                break
            spot += 1
        grid[move][spot] = p.mark

    

