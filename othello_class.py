class othello:
    def __init__(self, p1, p2, p1_theme = "dark", p2_theme = "dark"):
        self.items = []
        self.board = ""
        self.winner = None
        self.tie = False
        self.p1 = p1
        self.p2 = p2
        self.game_end = 0
        self.turn = 0
        self.p1_theme = p1_theme
        self.p2_theme = p2_theme
        temp = []
        self.lines = []
        for x in range(1, 65):
            temp.append("")
            if x % 8 == 0:
                self.items.append(temp)
                temp = []
        self.items[3][3] = "black"
        self.items[3][4] = "white"
        self.items[4][3] = "white"
        self.items[4][4] = "black"
        
    def string_rows(self):
        if self.turn == 0:
            if self.p1_theme == "dark":
                box = "⬛"
            else:
                box = "⬜"
        else:
            if self.p2_theme == "dark":
                box = "⬛"
            else:
                box = "⬜"
        self.board = f'''{box}{box}1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣
'''
        self.board += box*10
        self.board += '''
'''
        for i in range(len(self.items)):
            ind = i+1
            if ind == 1:
                self.board += "1️⃣"
            elif ind == 2:
                self.board += "2️⃣"
            elif ind == 3:
                self.board += "3️⃣"
            elif ind == 4:
                self.board += "4️⃣"
            elif ind == 5:
                self.board += "5️⃣"
            elif ind == 6:
                self.board += "6️⃣"
            elif ind == 7:
                self.board += "7️⃣"
            elif ind == 8:
                self.board += "8️⃣"
            self.board += box
            x = self.items[i]
            for y in x:
                if y == "":
                    self.board += "🟢"
                elif y == "black":
                    self.board += "⚫"
                else:
                    self.board += "⚪"
            self.board += '''
'''

    def form_lines(self, r, c):
        self.lines = []
        line = []
        temp_r = r+1
        temp_c = c
        while temp_r < 9:
            line.append((temp_r, temp_c))
            temp_r += 1
        self.lines.append(line)
        line = []
        temp_r = r-1
        temp_c = c
        while temp_r > 0:
            line.append((temp_r, temp_c))
            temp_r -= 1
        self.lines.append(line)
        line = []
        temp_r = r
        temp_c = c+1
        while temp_c < 9:
            line.append((temp_r, temp_c))
            temp_c += 1
        self.lines.append(line)
        line = []
        temp_r = r
        temp_c = c-1
        while temp_c > 0:
            line.append((temp_r, temp_c))
            temp_c -= 1
        self.lines.append(line)
        line = []
        temp_r = r+1
        temp_c = c+1
        while temp_r < 9 and temp_c < 9:
            line.append((temp_r, temp_c))
            temp_r += 1
            temp_c += 1
        self.lines.append(line)
        line = []
        temp_r = r+1
        temp_c = c-1
        while temp_r < 9 and temp_c > 0:
            line.append((temp_r, temp_c))
            temp_r += 1
            temp_c -= 1
        self.lines.append(line)
        line = []
        temp_r = r-1
        temp_c = c+1
        while temp_r > 0 and temp_c < 9:
            line.append((temp_r, temp_c))
            temp_r -= 1
            temp_c += 1
        self.lines.append(line)
        line = []
        temp_r = r-1
        temp_c = c-1
        while temp_r > 0 and temp_c > 0:
            line.append((temp_r, temp_c))
            temp_r -= 1
            temp_c -= 1
        self.lines.append(line)

    def any_valid(self, colour):
        for i in range(len(self.items)):
            row = self.items[i]
            for ind in range(len(row)):
                item = row[ind]
                if item == "":
                    if self.is_valid_move(i+1, ind+1, colour):
                        return True
        return False

    def is_valid_move(self, r, c, colour):
        self.form_lines(r, c)
        is_valid = False
        is_valid_temp = False
        if self.items[r-1][c-1] == "":
            for i in range(len(self.lines)):
                line = self.lines[i]
                for ind in range(len(line)):
                    pos = line[ind]
                    item = self.items[pos[0]-1][pos[1]-1]
                    if ind != 0 and item == colour:
                        self.lines[i] = (line, True)
                        is_valid = True
                        is_valid_temp = True
                    if item in ["", colour]:
                        break
                if not is_valid_temp:
                    self.lines[i] = (line, False)
                is_valid_temp = False
        return is_valid
    
    def guess(self, r, c, colour):
        if self.is_valid_move(r, c, colour):
            self.items[r-1][c-1] = colour
            for line in self.lines:
                if line[1]:
                    for ind in range(len(line[0])):
                        pos = line[0][ind]
                        item = self.items[pos[0]-1][pos[1]-1]
                        if item not in ["", colour]:
                            self.items[pos[0]-1][pos[1]-1] = colour
                        else:
                            break
    
    def find_winner(self):
        black_points = 0
        white_points = 0
        for x in self.items:
            for y in x:
                if y == "black":
                    black_points += 1
                elif y == "white":
                    white_points += 1
        if black_points > white_points:
            self.winner = self.p1
        elif white_points > black_points:
            self.winner = self.p2
        else:
            self.tie = True
        self.game_end = 1