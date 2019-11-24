from connect4 import *
from player import *

players = []
players.append(Connect4Manual('y'))
players.append(Connect4Manual('r'))

grid = []
for i in range(7):
    column = []
    for j in range(6):
        column.append('')
    grid.append(column)

while True:
    for p in players:
        move = p.play(grid)
        spot = 0
        while grid[move][spot] != '':
            if spot == 5:
                print("tried to add to full column")
                break
            spot += 1
        grid[move][spot] = p.mark

    

