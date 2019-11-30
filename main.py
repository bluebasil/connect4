from connect4 import *
from player import *
from copy import deepcopy
from connect4TimeSensitivey import Connect4 as connect4TS
from datetime import datetime, timedelta

def print_grid(grid):

    #for col in grid:
    #    print(col)
    print("---------")
    for row_num in range(5,-1,-1):
        row = [column[row_num] for column in grid]
        print("|", end='')
        for c in row:
            s = " "
            if c == 'y':
                #sys.stdout.buffer.write(TestText2)
                s = chr(48)
                #s = b'●'
            elif c == 'r':
                #sys.stdout.buffer.write(TestText2)
                s = chr(160)
                #s = b'○'
            print(s,end='')
        print("|")
    print("|0123456|", flush=True)

def check_win(grid):
    for column in grid:
        winner = check_line(column)
        if winner is not None:
            return winner

    for row_num in range(6):
        row = [column[row_num] for column in grid]
        winner = check_line(row)
        if winner is not None:
            return winner

    for diag_1 in range(3,10):
        column = min(diag_1, 6)
        line = []
        while column >= 0 and diag_1-column < 6:
            #print(f"Out of range {len(grid)} {column}, {len(grid[column])} {diag_1}")
            line.append(grid[column][diag_1-column])
            column -= 1
        winner = check_line(line)
        if winner is not None:
            return winner

    for diag_2 in range(3,10):
        column = min(diag_2, 6)
        line = []
        while column >= 0 and diag_2-column < 6:
            line.append(grid[6-column][diag_2-column])
            column -= 1
        winner = check_line(line)
        if winner is not None:
            return winner

    return None

def check_line(line):
    for i in range(len(line)-3):
        winner = check_line_sebset(line[i:i+4])
        if winner is not None:
            #print(f"winning line: {winner}")
            #print(line[i:i+4])
            return winner

def check_line_sebset(cells):
    test_winner = cells[0]
    if test_winner == '':
        return None
    for c in cells:
        if c != test_winner:
            return None
    return test_winner




# y high

players = []
#players.append(Connect4Manual('y'))
#players.append(Connect4Manual('r'))


players.append(connect4TS('r'))
players.append(connect4TS('y'))

grid = []
for i in range(7):
    column = []
    for j in range(6):
        column.append('')
    grid.append(column)

#grid = [
#        ['y','r','y','r','',''],
#        ['y','r','y','r','',''],
#        ['r','y','r','y','',''],
#        ['r','y','r','y','',''],
##        ['y','r','y','r','',''],
#        ['y','r','y','r','',''],
#        ['r','y','r','y','','']
#        ]

while True:
    for p in players:
        print_grid(grid)
        if check_win(grid) is not None:
            print(check_win(grid), " wins")
            exit()
        temp_grid = deepcopy(grid)
        print("Start: ", datetime.now(), flush=True)
        move = p.play(temp_grid)
        print("End: ", datetime.now(), flush=True)
        spot = 0
        while grid[move][spot] != '':
            if spot == 5:
                print("tried to add to full column: ", move)
                print(grid)
                exit()
                break
            spot += 1
        grid[move][spot] = p.mark
        


    

