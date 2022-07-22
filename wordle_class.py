class wordle:
    def __init__(self, p1, p2, p2_theme):
        self.hword = []
        self.gword = []
        self.gwords = []
        self.pos = []
        self.positions = []
        self.letters = {"a": ":regional_indicator_a:", "b": ":regional_indicator_b:", "c": ":regional_indicator_c:", "d": ":regional_indicator_d:", "e": ":regional_indicator_e:", "f": ":regional_indicator_f:", "g": ":regional_indicator_g:", "h": ":regional_indicator_h:", "i": ":regional_indicator_i:", "j": ":regional_indicator_j:", "k": ":regional_indicator_k:", "l": ":regional_indicator_l:", "m": ":regional_indicator_m:", "n": ":regional_indicator_n:", "o": ":regional_indicator_o:", "p": ":regional_indicator_p:", "q": ":regional_indicator_q:", "r": ":regional_indicator_r:", "s": ":regional_indicator_s:", "t": ":regional_indicator_t:", "u": ":regional_indicator_u:", "v": ":regional_indicator_v:", "w": ":regional_indicator_w:", "x": ":regional_indicator_x:", "y": ":regional_indicator_y:", "z": ":regional_indicator_z:"}
        self.keyboard = {":regional_indicator_a:": "Empty", ":regional_indicator_b:": "Empty", ":regional_indicator_c:": "Empty", ":regional_indicator_d:": "Empty", ":regional_indicator_e:": "Empty", ":regional_indicator_f:": "Empty", ":regional_indicator_g:": "Empty", ":regional_indicator_h:": "Empty", ":regional_indicator_i:": "Empty", ":regional_indicator_j:": "Empty", ":regional_indicator_k:": "Empty", ":regional_indicator_l:": "Empty", ":regional_indicator_m:": "Empty", ":regional_indicator_n:": "Empty", ":regional_indicator_o:": "Empty", ":regional_indicator_p:": "Empty", ":regional_indicator_q:": "Empty", ":regional_indicator_r:": "Empty", ":regional_indicator_s:": "Empty", ":regional_indicator_t:": "Empty", ":regional_indicator_u:": "Empty", ":regional_indicator_v:": "Empty", ":regional_indicator_w:": "Empty", ":regional_indicator_x:": "Empty", ":regional_indicator_y:": "Empty", ":regional_indicator_z:": "Empty"}
        self.keyboard_string = ""
        self.game = 0
        self.turns = 0
        self.grid = ""
        self.p1 = p1
        self.p2 = p2
        self.p2_theme = p2_theme
        self.winner = None

    def string_rows(self):
        if self.p2_theme == "dark":
            button = "🔳"
            box = "⬛"
            box_inv = "⬜"
        else:
            button = "🔲"
            box = "⬜"
            box_inv = "⬛"
        
        self.grid = ""
        self.keyboard_string = ""
        if self.game == 0 and self.turns != 6:
            self.grid += button*5+box*6
        else:
            self.grid += "||"
            for piece in self.hword:
                self.grid += piece
            self.grid += "||"
            self.grid += box*6
        self.grid += '''
'''
        self.grid += box*11
        self.grid += '''
'''
        for ind in range(len(self.gwords)):
            gword = self.gwords[ind]
            positions = self.positions[ind]
            for piece in gword:
                self.grid += piece
            self.grid += box
            for b in positions:
                if b == "Bull":
                    pos = "🟩"
                elif b == "Cow":
                    pos = "🟨"
                elif b == "Dead":
                    pos = "🟥"
                self.grid += pos
            self.grid += '''
'''
        rem_rows = 6-len(self.gwords)
        for row in range(rem_rows):
            self.grid += box_inv*5 + box + box_inv*5
            self.grid += '''
'''

        for letter in self.keyboard.keys():
            if self.keyboard[letter] == "Bull":
                colour = "🟩"
            elif self.keyboard[letter] == "Cow":
                colour = "🟨"
            elif self.keyboard[letter] == "Dead":
                colour = "🟥"
            elif self.keyboard[letter] == "Empty":
                colour = box
            self.keyboard_string += f"{self.letters[letter[-2]]}{colour}|"

    def colourify(self, word, h):
        self.gword = []
        if h == 0:
            for letter in word:
                self.gword.append(self.letters[letter])
            self.gwords.append(self.gword)
        else:
            for letter in word:
                self.hword.append(self.letters[letter])

    def guess(self, word):
        self.colourify(word, 0)
        self.pos = []
        gword_temp = self.gword.copy()
        hword_temp = self.hword.copy()
        for ind in range(len(self.hword)):
            letter = self.hword[ind]
            if letter == self.gword[ind]:
                self.pos.append("Bull")
                gword_temp.pop(ind - (5-len(gword_temp)))
                hword_temp.pop(ind - (5-len(hword_temp)))
                self.keyboard[letter] = "Bull"
            else:
                self.pos.append(None)
        for x in gword_temp:
            if x in hword_temp:
                for y in range(len(self.pos)):
                    if self.pos[y] == None:
                        self.pos[y] = "Cow"
                        break
                hword_temp.remove(x)
                if self.keyboard[x] == "Empty":
                    self.keyboard[x] = "Cow"
            else:
                for y in range(len(self.pos)):
                    if self.pos[y] == None:
                        self.pos[y] = "Dead"
                        break
                if self.keyboard[x] == "Empty":
                    self.keyboard[x] = "Dead"
        self.positions.append(self.pos)
        if self.gword == self.hword:
            self.game = 1
            self.winner = self.p2
        else:
            self.turns += 1