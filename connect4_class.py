class connect4:
    def __init__(self, a_id, opp_id):
        self.columns = []
        self.temp = []
        self.turn = 0
        self.string_items = ""
        self.winner = None
        self.left_pos = 42
        self.game_end = 0
        self.p1 = a_id
        self.p2 = opp_id
        for x in range(1, 43):
            self.temp.append("")
            if x%6 == 0:
                self.columns.append(self.temp)
                self.temp = []
        
    def string_rows(self):
        self.string_items = ""
        self.string_items += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        self.string_items += '''
'''
        self.string_items += "⬛"*7
        for x in range(6):
            self.string_items += '''
'''
            for y in range(7):
                item = self.columns[y][5-x]
                if item == "Red":
                    self.string_items += "🔴"
                elif item == "Yellow":
                    self.string_items += "🟡"
                else:
                    self.string_items += "⚪"
    
    def game_over(self):
        for x in range(6):
            for y in range(7):
                row = 5-x
                obj = self.columns[y][row]
                if obj != "":
                    if row < 3:
                        list_objs = [self.columns[y][row], self.columns[y][row+1], self.columns[y][row+2], self.columns[y][row+3]]
                        if list_objs == [obj, obj, obj, obj]:
                            if obj == "Red":
                                self.winner = self.p1
                            else:
                                self.winner = self.p2
                            self.game_end = 1
                    if y < 4:
                        list_objs = [self.columns[y][row], self.columns[y+1][row], self.columns[y+2][row], self.columns[y+3][row]]
                        if list_objs == [obj, obj, obj, obj]:
                            if obj == "Red":
                                self.winner = self.p1
                            else:
                                self.winner = self.p2
                            self.game_end = 1
                    if row < 3 and y < 4:
                        list_objs = [self.columns[y][row], self.columns[y+1][row+1], self.columns[y+2][row+2], self.columns[y+3][row+3]]
                        if list_objs == [obj, obj, obj, obj]:
                            if obj == "Red":
                                self.winner = self.p1
                            else:
                                self.winner = self.p2
                            self.game_end = 1
                    if row < 3 and y > 2:
                        list_objs = [self.columns[y][row], self.columns[y-1][row+1], self.columns[y-2][row+2], self.columns[y-3][row+3]]
                        if list_objs == [obj, obj, obj, obj]:
                            if obj == "Red":
                                self.winner = self.p1
                            else:
                                self.winner = self.p2
                            self.game_end = 1