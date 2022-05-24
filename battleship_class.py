class battleship:
    def __init__(self, theme_1 = "dark", theme_2 = "dark"):
        self.ship_locs = []
        self.grid = []
        self.grid_string = ""
        self.guess_string = ""
        self.alive_ships = 5
        self.ship_names = ""
        for x in range(10):
            row = []
            for y in range(10):
                row.append("alive")
            self.grid.append(row)
        if theme_1 == "dark":
            self.box_1 = "⬛"
            self.box_1_ulta = "🔳"
        else:
            self.box_1 = "⬜"
            self.box_1_ulta = "🔲"
        if theme_2 == "dark":
            self.box_2 = "⬛"
            self.box_2_ulta = "🔳"
        else:
            self.box_2 = "⬜"
            self.box_2_ulta = "🔲"
        
    
    def string_grid(self):
        self.ship_names = ""
        for ind in range(len(self.ship_locs)):
            if self.ship_locs[ind][1] == "dead":
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"~~{ship}~~"
            else:
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"{ship}"
            self.ship_names += ", "
        self.ship_names = self.ship_names[0:-2]
        self.grid_string = ""
        self.grid_string += f"{self.box_1}{self.box_1}1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟"
        self.grid_string += '''
'''
        self.grid_string += self.box_1*12
        self.grid_string += '''
'''
        c = 1
        for row in self.grid:
            if c == 1:
                self.grid_string += "1️⃣"
            elif c == 2:
                self.grid_string += "2️⃣"
            elif c == 3:
                self.grid_string += "3️⃣"
            elif c == 4:
                self.grid_string += "4️⃣"
            elif c == 5:
                self.grid_string += "5️⃣"
            elif c == 6:
                self.grid_string += "6️⃣"
            elif c == 7:
                self.grid_string += "7️⃣"
            elif c == 8:
                self.grid_string += "8️⃣"
            elif c == 9:
                self.grid_string += "9️⃣"
            elif c == 10:
                self.grid_string += "🔟"
            self.grid_string += self.box_1
            for p in row:
                if p == "alive":
                    self.grid_string += "🟦"
                elif p == "occupied":
                    self.grid_string += self.box_1_ulta
                elif p == "dead":
                    self.grid_string += "⏺"
                elif p == "shot":
                    self.grid_string += "🔥"
                elif p == "destroyed":
                    self.grid_string += "❌"
            self.grid_string += '''
'''
            c += 1

    def final_grid(self):
        self.ship_names = ""
        for ind in range(len(self.ship_locs)):
            if self.ship_locs[ind][1] == "dead":
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"~~{ship}~~"
            else:
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"{ship}"
            self.ship_names += ", "
        self.ship_names = self.ship_names[0:-2]
        self.grid_string = ""
        self.grid_string += f"{self.box_2}{self.box_2}1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟"
        self.grid_string += '''
'''
        self.grid_string += self.box_2*12
        self.grid_string += '''
'''
        c = 1
        for row in self.grid:
            if c == 1:
                self.grid_string += "1️⃣"
            elif c == 2:
                self.grid_string += "2️⃣"
            elif c == 3:
                self.grid_string += "3️⃣"
            elif c == 4:
                self.grid_string += "4️⃣"
            elif c == 5:
                self.grid_string += "5️⃣"
            elif c == 6:
                self.grid_string += "6️⃣"
            elif c == 7:
                self.grid_string += "7️⃣"
            elif c == 8:
                self.grid_string += "8️⃣"
            elif c == 9:
                self.grid_string += "9️⃣"
            elif c == 10:
                self.grid_string += "🔟"
            self.grid_string += self.box_2
            for p in row:
                if p == "alive":
                    self.grid_string += "🟦"
                elif p == "occupied":
                    self.grid_string += self.box_2_ulta
                elif p == "dead":
                    self.grid_string += "⏺"
                elif p == "shot":
                    self.grid_string += "🔥"
                elif p == "destroyed":
                    self.grid_string += "❌"
            self.grid_string += '''
'''
            c += 1

    def string_guess(self):
        self.ship_names = ""
        for ind in range(len(self.ship_locs)):
            if self.ship_locs[ind][1] == "dead":
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"~~{ship}~~"
            else:
                if ind == 0:
                    ship = "Carrier (5)"
                elif ind == 1:
                    ship = "Battleship (4)"
                elif ind == 2:
                    ship = "Cruiser (3)"
                elif ind == 3:
                    ship = "Submarine (3)"
                elif ind == 4:
                    ship = "Destroyer (2)"
                self.ship_names += f"{ship}"
            self.ship_names += ", "
        self.ship_names = self.ship_names[0:-2]
        self.guess_string = ""
        self.guess_string = ""
        self.guess_string += f"{self.box_2}{self.box_2}1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟"
        self.guess_string += '''
'''
        self.guess_string += self.box_2*12
        self.guess_string += '''
'''
        c = 1
        for row in self.grid:
            if c == 1:
                self.guess_string += "1️⃣"
            elif c == 2:
                self.guess_string += "2️⃣"
            elif c == 3:
                self.guess_string += "3️⃣"
            elif c == 4:
                self.guess_string += "4️⃣"
            elif c == 5:
                self.guess_string += "5️⃣"
            elif c == 6:
                self.guess_string += "6️⃣"
            elif c == 7:
                self.guess_string += "7️⃣"
            elif c == 8:
                self.guess_string += "8️⃣"
            elif c == 9:
                self.guess_string += "9️⃣"
            elif c == 10:
                self.guess_string += "🔟"
            self.guess_string += self.box_2
            for p in row:
                if p == "alive" or p == "occupied":
                    self.guess_string += "🟦"
                elif p == "dead":
                    self.guess_string += "⏺"
                elif p == "shot":
                    self.guess_string += "🔥"
                elif p == "destroyed":
                    self.guess_string += "❌"
            self.guess_string += '''
'''
            c += 1

    def valid_ship(self, loc, length):
        invalid = 0
        error = ""
        loc_1 = loc[0]
        loc_2 = loc[1]
        if loc_1[0] == loc_2[0]:
            if abs(loc_1[1] - loc_2[1])+1 != length:
                invalid = 1
                error = "length"
        elif loc_1[1] == loc_2[1]:
            if abs(loc_1[0] - loc_2[0])+1 != length:
                invalid = 1
                error = "length"
        else:
            invalid = 1
            error = "row"
        if invalid == 0:
            if loc_1[0] == loc_2[0]:
                i = loc_1[1]
                f = loc_2[1]
                if i > f:
                    temp = i
                    i = f
                    f = temp
                for x in range(length):
                    if self.grid[loc_1[0]-1][i-1] == "occupied":
                        invalid = 1
                        error = "overlap"
                        break
                    i += 1
            else:
                i = loc_1[0]
                f = loc_2[0]
                if i > f:
                    temp = i
                    i = f
                    f = temp
                for x in range(length):
                    if self.grid[i-1][loc_1[1]-1] == "occupied":
                        invalid = 1
                        error = "overlap"
                        break
                    i += 1
        return invalid, error
    
    def place_ship(self, loc, length):
        loc_1 = loc[0]
        loc_2 = loc[1]
        ship_loc = []
        if loc_1[0] == loc_2[0]:
            i = loc_1[1]
            f = loc_2[1]
            if i > f:
                temp = i
                i = f
                f = temp
            for x in range(length):
                self.grid[loc_1[0]-1][i-1] = "occupied"
                ship_loc.append((loc_1[0], i))
                i += 1
        else:
            i = loc_1[0]
            f = loc_2[0]
            if i > f:
                temp = i
                i = f
                f = temp
            for x in range(length):
                self.grid[i-1][loc_1[1]-1] = "occupied"
                ship_loc.append((i, loc_1[1]))
                i += 1
        self.ship_locs.append([ship_loc, "alive"])
    
    def shoot(self, loc):
        shot = 0
        invalid = 0
        destroyed = 0
        ship = ""
        if self.grid[loc[0]-1][loc[1]-1] == "alive" or self.grid[loc[0]-1][loc[1]-1] == "occupied":
            if self.grid[loc[0]-1][loc[1]-1] == "occupied":
                shot = 1
                self.grid[loc[0]-1][loc[1]-1] = "shot"
                for ind in range(len(self.ship_locs)):
                    ship = self.ship_locs[ind]
                    new_dead = False
                    if ship[1] != "dead":
                        new_dead = True
                        for x in ship[0]:
                            if self.grid[x[0]-1][x[1]-1] == "occupied":
                                new_dead = False
                                break
                        if new_dead:
                            self.alive_ships -= 1
                            destroyed = 1
                            self.ship_locs[ind][1] = "dead"
                            for x in self.ship_locs[ind][0]:
                                self.grid[x[0]-1][x[1]-1] = "destroyed"
                flag = 0
                for ind in range(len(self.ship_locs)):
                    if flag == 0:
                        for t in self.ship_locs[ind][0]:
                            if loc == t:
                                if ind == 0:
                                    ship = "carrier"
                                elif ind == 1:
                                    ship = "battleship"
                                elif ind == 2:
                                    ship = "cruiser"
                                elif ind == 3:
                                    ship = "submarine"
                                elif ind == 4:
                                    ship = "destroyer"
                                flag = 1
                                break
                    else:
                        break
            else:
                self.grid[loc[0]-1][loc[1]-1] = "dead"
        else:
            invalid = 1
        return invalid, shot, destroyed, ship