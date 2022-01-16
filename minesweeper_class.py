import random as rd
import time
from records import stats_update, score_check
class minesweeper:
    def __init__(self, num_rows = 8, num_cols = 8, num_bombs = 8, user_id = 0):
        self.user_id = user_id
        self.time_start = time.time()
        self.flag_var = 0
        self.items = []
        self.items_g = []
        self.items_stat = []
        self.str_row = ""
        self.game = 1
        self.turns = 0
        self.items_tot = num_rows*num_cols
        self.row_brk = []
        self.row_brk_g = []
        self.items_stat_row = []
        self.game_over = 0
        self.end_msg = ""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_bombs = num_bombs
        self.flag = "Off"
        self.bomb_list = []
        self.flag_pos = []

        for x in range(1, self.items_tot+1):
            self.row_brk.append("")
            self.row_brk_g.append("")
            self.items_stat_row.append("alive")
            if x % self.num_cols == 0:
                self.items.append(self.row_brk)
                self.items_g.append(self.row_brk_g)
                self.items_stat.append(self.items_stat_row)
                self.row_brk = []
                self.row_brk_g = []
                self.items_stat_row = []
        choice_row = []
        self.row_c = 1
        for y in range(0, self.num_rows):
            choice_row.append(self.row_c)
            self.row_c += 1

        choice_column = []
        self.col_c = 1
        for z in range(0, self.num_cols):
            choice_column.append(self.col_c)
            self.col_c += 1

        for b in range(0, self.num_bombs):
            self.row_pos = rd.choice(choice_row)
            self.col_pos = rd.choice(choice_column)
            while self.items[self.row_pos-1][self.col_pos-1] == "💥":
                self.row_pos = rd.choice(choice_row)
                self.col_pos = rd.choice(choice_column)
            self.items[self.row_pos-1][self.col_pos-1] = "💥"
            self.bomb_list.append((self.row_pos, self.col_pos))

        for row in range(1, self.num_rows+1):
            for col in range(1, self.num_cols+1):
                num = 0
                if self.items[row-1][col-1] != "💥":
                    if row != 1 and row != self.num_rows and col != 1 and col != self.num_cols:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row][col] == "💥":
                            num += 1
                        if self.items[row][col-2] == "💥":
                            num += 1
                        if self.items[row-2][col] == "💥":
                            num += 1
                        if self.items[row-2][col-2] == "💥":
                            num += 1

                    elif row == 1 and col != 1 and col != self.num_cols:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row][col] == "💥":
                            num += 1
                        if self.items[row][col-2] == "💥":
                            num += 1

                    elif row == self.num_rows and col != 1 and col != self.num_cols:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col] == "💥":
                            num += 1
                        if self.items[row-2][col-2] == "💥":
                            num += 1

                    elif col == 1 and row != 1 and row != self.num_rows:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row][col] == "💥":
                            num += 1
                        if self.items[row-2][col] == "💥":
                            num += 1

                    elif col == self.num_cols and row != 1 and row != self.num_rows:
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row][col-2] == "💥":
                            num += 1
                        if self.items[row-2][col-2] == "💥":
                            num += 1

                    if row == 1 and col == 1:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row][col] == "💥":
                            num += 1

                    if row == 1 and col == self.num_cols:
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row][col-1] == "💥":
                            num += 1
                        if self.items[row][col-2] == "💥":
                            num += 1

                    if row == self.num_rows and col == 1:
                        if self.items[row-1][col] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col] == "💥":
                            num += 1

                    if row == self.num_rows and col == self.num_cols:
                        if self.items[row-1][col-2] == "💥":
                            num += 1
                        if self.items[row-2][col-1] == "💥":
                            num += 1
                        if self.items[row-2][col-2] == "💥":
                            num += 1

                    self.items[row-1][col-1] = num
        self.string_rows()


    def string_rows(self):
        if self.game_over == 1:
            for bomb_pos in self.bomb_list:
                if self.items_g[bomb_pos[0]-1][bomb_pos[1]-1] != "🚩":
                    self.items_g[bomb_pos[0]-1][bomb_pos[1]-1] = "⚠"
            for flag_p in self.flag_pos:
                if flag_p not in self.bomb_list:
                    self.items_g[flag_p[0]-1][flag_p[1]-1] = "❌"
                else:
                    self.items_g[bomb_pos[0]-1][bomb_pos[1]-1] = "✔"
        self.str_row = '''
'''
        for i in range(len(str(self.num_cols))+1):
            self.str_row += "⬛"*(len(str(self.num_rows))+1)
            for x in range(1, self.num_cols+1):
                r = str(x)
                if len(r) == 1:
                    r += " "
                if len(str(self.num_cols)) == 2:
                    r += " "
                if r[i] == " ":
                    self.str_row += "⬛"
                elif r[i] == "1":
                    self.str_row += "1️⃣"
                elif r[i] == "2":
                    self.str_row += "2️⃣"
                elif r[i] == "3":
                    self.str_row += "3️⃣"
                elif r[i] == "4":
                    self.str_row += "4️⃣"
                elif r[i] == "5":
                    self.str_row += "5️⃣"
                elif r[i] == "6":
                    self.str_row += "6️⃣"
                elif r[i] == "7":
                    self.str_row += "7️⃣"
                elif r[i] == "8":
                    self.str_row += "8️⃣"
                elif r[i] == "9":
                    self.str_row += "9️⃣"
                elif r[i] == "0":
                    self.str_row += "0️⃣"
            self.str_row += '''
'''
        row = 1
        self.str_row += "1️⃣"
        self.str_row += "⬛"*len(str(self.num_rows))
        for ro in range(0, self.num_rows):
            for col in range(0, self.num_cols):
                item = self.items_g[ro][col]
                if item == "":
                    item = "⚪"
                elif item == 1:
                    item = "1️⃣"
                elif item == 2:
                    item = "2️⃣"
                elif item == 3:
                    item = "3️⃣"
                elif item == 4:
                    item = "4️⃣"
                elif item == 5:
                    item = "5️⃣"
                elif item == 6:
                    item = "6️⃣"
                elif item == 7:
                    item = "7️⃣"
                elif item == 8:
                    item = "8️⃣"
                elif item == 0:
                    item = "🟦"
                self.str_row += item

            self.str_row += '''
'''
            if ro != self.num_rows-1:
                row += 1
                r = str(row)
                if len(r) == 1 and self.num_rows >= 10:
                    r += " "
                for i in r:
                    if i == " ":
                        self.str_row += "⬛"
                    elif i == "1":
                        self.str_row += "1️⃣"
                    elif i == "2":
                        self.str_row += "2️⃣"
                    elif i == "3":
                        self.str_row += "3️⃣"
                    elif i == "4":
                        self.str_row += "4️⃣"
                    elif i == "5":
                        self.str_row += "5️⃣"
                    elif i == "6":
                        self.str_row += "6️⃣"
                    elif i == "7":
                        self.str_row += "7️⃣"
                    elif i == "8":
                        self.str_row += "8️⃣"
                    elif i == "9":
                        self.str_row += "9️⃣"
                    elif i == "0":
                        self.str_row += "0️⃣"

                self.str_row += "⬛"


    def guess(self, r, c):
        if self.flag_var == 0:
            if self.items_stat[r-1][c-1] == "alive":
                obj = self.items[r-1][c-1]
                self.items_g[r-1][c-1] = obj
                self.items_stat[r-1][c-1] = "dead"
            if obj == "💥":
                self.game_over = 1
                self.bomb_list.remove((r, c))
            self.string_rows()
            self.turns += 1
            self.game_end()

            if obj == 0:
                if r != 1 and r != self.num_rows and c != 1 and c != self.num_cols:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r][c] == "alive":
                        self.guess(r+1, c+1)
                    if self.items_stat[r][c-2] == "alive":
                        self.guess(r+1, c-1)
                    if self.items_stat[r-2][c] == "alive":
                        self.guess(r-1, c+1)
                    if self.items_stat[r-2][c-2] == "alive":
                        self.guess(r-1, c-1)

                elif r == 1 and c != 1 and c != self.num_cols:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r][c] == "alive":
                        self.guess(r+1, c+1)
                    if self.items_stat[r][c-2] == "alive":
                        self.guess(r+1, c-1)

                elif r == self.num_rows and c != 1 and c != self.num_cols:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r-2][c] == "alive":
                        self.guess(r-1, c+1)
                    if self.items_stat[r-2][c-2] == "alive":
                        self.guess(r-1, c-1)

                elif c == 1 and r != 1 and r != self.num_rows:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r][c] == "alive":
                        self.guess(r+1, c+1)
                    if self.items_stat[r-2][c] == "alive":
                        self.guess(r-1, c+1)

                elif c == self.num_cols and r != 1 and r != self.num_rows:
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r][c-2] == "alive":
                        self.guess(r+1, c-1)
                    if self.items_stat[r-2][c-2] == "alive":
                        self.guess(r-1, c-1)

                elif r == 1 and c == 1:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r][c] == "alive":
                        self.guess(r+1, c+1)

                elif r == 1 and c == self.num_cols:
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r][c-1] == "alive":
                        self.guess(r+1, c)
                    if self.items_stat[r][c-2] == "alive":
                        self.guess(r+1, c-1)

                elif r == self.num_rows and c == 1:
                    if self.items_stat[r-1][c] == "alive":
                        self.guess(r, c+1)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r-2][c] == "alive":
                        self.guess(r-1, c+1)

                elif r == self.num_rows and c == self.num_cols:
                    if self.items_stat[r-1][c-2] == "alive":
                        self.guess(r, c-1)
                    if self.items_stat[r-2][c-1] == "alive":
                        self.guess(r-1, c)
                    if self.items_stat[r-2][c-2] == "alive":
                        self.guess(r-1, c-1)
        else:
            if self.items_stat[r-1][c-1] == "alive":
                if self.items_g[r-1][c-1] == "":
                    self.items_g[r-1][c-1] = "🚩"
                    self.flag_pos.append((r, c))
                elif self.items_g[r-1][c-1] == "🚩":
                    self.items_g[r-1][c-1] = ""
                    self.flag_pos.remove((r, c))
            else:
                raise UnboundLocalError
            self.string_rows()

    def game_end(self):
        if self.game_over == 1:
            self.end_msg = "You lost 😢"
            self.game = 0
            stats_update(self.user_id, 0)
        elif self.turns == (self.items_tot-self.num_bombs):
            if self.num_rows == 8 and self.num_cols == 8 and self.num_bombs == 8:
                self.time_end = time.time()
                self.tot_time = int(self.time_end-self.time_start)
                self.mins = int(self.tot_time//60)
                self.secs = int(self.tot_time%60)
                stats_update(self.user_id, 1)
                if score_check(self.user_id, self.tot_time) not in ["new high", "new record"]:
                    self.end_msg = '''You won 🥳
Time taken: '''+str(self.mins)+"m and "+str(self.secs)+"s"
                else:
                    self.end_msg = '''You won 🥳
Time taken: '''+str(self.mins)+"m and "+str(self.secs)+"s"+'''
You made a new record!'''
            else:
                self.end_msg = "You won 🥳"
            self.game = 0