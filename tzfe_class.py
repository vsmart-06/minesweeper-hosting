import random as rd
from copy import deepcopy

class tzfe:
    def __init__(self, a, b, c, d, e, f, g, h, i, j, k, theme):
        self.grid = [[[None, False], [None, False], [None, False], [None, False]], [[None, False], [None, False], [None, False], [None, False]], [[None, False], [None, False], [None, False], [None, False]], [[None, False], [None, False], [None, False], [None, False]]]
        self.game_board = ""
        if theme == "dark":
            button = "🔳"
        else:
            button = "🔲"
        self.emojis = {2: a, 4: b, 8: c, 16: d, 32: e, 64: f, 128: g, 256: h, 512: i, 1024: j, 2048: k, None: button}
        self.score = 0
        self.grid[rd.randint(0, 3)][rd.randint(0, 3)] = [rd.choice([2, 2, 2, 2, 2, 2, 2, 2, 2, 4]), False]
        while True:
            r = rd.randint(0, 3)
            c = rd.randint(0, 3)
            if self.grid[r][c][0] == None:
                self.grid[r][c] = [rd.choice([2, 2, 2, 2, 2, 2, 2, 2, 2, 4]), False]
                break
        self.game = 1

    def string_rows(self):
        self.game_board = ""
        for x in self.grid:
            for y in x:
                self.game_board += f"{self.emojis[y[0]]}"
            self.game_board += "\n"
        

    def swipe(self, dir):
        old_grid = deepcopy(self.grid)
        def in_swipe(grid, dir):
            old_grid = deepcopy(grid)
            if dir == "up":
                for i in range(4):
                    for j in range(4):
                        item = grid[i][j]
                        num = grid[i][j][0]
                        if num != None:
                            if i != 0:
                                if grid[i-1][j][0] == None:
                                    grid[i-1][j] = [num, item[1]]
                                    grid[i][j] = [None, False]
                                elif grid[i-1][j][0] == num and item[1] == False and grid[i-1][j][1] == False:
                                    grid[i-1][j] = [2*num, True]
                                    self.score += 2*num
                                    grid[i][j] = [None, False]
                                    if 2*num == 2048:
                                        self.game = 0
            elif dir == "down":
                for i in range(3, -1 , -1):
                    for j in range(4):
                        item = grid[i][j]
                        num = grid[i][j][0]
                        if num != None:
                            if i != 3:
                                if grid[i+1][j][0] == None:
                                    grid[i+1][j] = [num, item[1]]
                                    grid[i][j] = [None, False]
                                elif grid[i+1][j][0] == num and item[1] == False and grid[i+1][j][1] == False:
                                    grid[i+1][j] = [2*num, True]
                                    self.score += 2*num
                                    grid[i][j] =  [None, False]
                                    if 2*num == 2048:
                                        self.game = 0
            elif dir == "left":
                for i in range(4):
                    for j in range(4):
                        item = grid[i][j]
                        num = grid[i][j][0]
                        if num != None:
                            if j != 0:
                                if grid[i][j-1][0] == None:
                                    grid[i][j-1] = [num, item[1]]
                                    grid[i][j] = [None, False]
                                elif grid[i][j-1][0] == num and item[1] == False and grid[i][j-1][1] == False:
                                    grid[i][j-1] = [2*num, True]
                                    self.score += 2*num
                                    grid[i][j] = [None, False]
                                    if 2*num == 2048:
                                        self.game = 0
            elif dir == "right":
                for i in range(4):
                    for j in range(3, -1, -1):
                        item = grid[i][j]
                        num = grid[i][j][0]
                        if num != None:
                            if j != 3:
                                if grid[i][j+1][0] == None:
                                    grid[i][j+1] = [num, item[1]]
                                    grid[i][j] = [None, False]
                                elif grid[i][j+1][0] == num and item[1] == False and grid[i][j+1][1] == False:
                                    grid[i][j+1] = [2*num, True]
                                    self.score += 2*num
                                    grid[i][j] = [None, False]
                                    if 2*num == 2048:
                                        self.game = 0
            if old_grid != grid:
                in_swipe(grid, dir)
            return grid
        self.grid = in_swipe(self.grid, dir)
        if old_grid != self.grid:
            empty_spots = []
            for i in range(4):
                for j in range(4):
                    if self.grid[i][j][0] == None:
                        empty_spots.append([i, j])
                    self.grid[i][j] = [self.grid[i][j][0], False]
            new_spot = rd.choice(empty_spots)
            self.grid[new_spot[0]][new_spot[1]] = [rd.choice([2, 2, 2, 2, 2, 2, 2, 2, 2, 4]), False]        
    
    def game_over(self):
        no_move = True
        for i in range(4):
            for j in range(4):
                num = self.grid[i][j][0]
                if num == None:
                    no_move = False
                elif i == 0 and j == 0:
                    if num in [self.grid[i+1][j][0], self.grid[i][j+1][0]]:
                        no_move = False
                elif i == 0 and j == 3:
                    if num in [self.grid[i+1][j][0], self.grid[i][j-1][0]]:
                        no_move = False
                elif i == 3 and j == 0:
                    if num in [self.grid[i-1][j][0], self.grid[i][j+1][0]]:
                        no_move = False
                elif i == 3 and j == 3:
                    if num in [self.grid[i-1][j][0], self.grid[i][j-1][0]]:
                        no_move = False
                elif i == 0:
                    if num in [self.grid[i][j-1][0], self.grid[i+1][j][0], self.grid[i][j+1][0]]:
                        no_move = False
                elif i == 3:
                    if num in [self.grid[i][j-1][0], self.grid[i-1][j][0], self.grid[i][j+1][0]]:
                        no_move = False
                elif j == 0:
                    if num in [self.grid[i-1][j][0], self.grid[i][j+1][0], self.grid[i+1][j][0]]:
                        no_move = False
                elif j == 3:
                    if num in [self.grid[i-1][j][0], self.grid[i][j-1][0], self.grid[i+1][j][0]]:
                        no_move = False
                else:
                    if num in [self.grid[i][j-1][0], self.grid[i-1][j][0], self.grid[i][j+1][0], self.grid[i+1][j]]:
                        no_move = False  
        if no_move:
            self.game = 0