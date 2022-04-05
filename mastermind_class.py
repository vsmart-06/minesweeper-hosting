import random as rd

class mastermind:
    def __init__(self, p1, p2, p2_theme):
        self.hcode = []
        self.gcode = []
        self.gcodes = []
        self.colour_list = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵", 6: "🟣", 7: "🟤"}
        self.pos = []
        self.positions = []
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
            circle = "⚪"
        else:
            button = "🔲"
            box = "⬜"
            box_inv = "⬛"
            circle = "⚫"

        self.grid = ""
        if self.game == 0:
            self.grid += button*4 + box*5
        else:
            self.grid += "||"
            for piece in self.hcode:
                self.grid += piece
            self.grid += "||"
            self.grid += box*5
        self.grid += '''
'''
        self.grid += box*9
        self.grid += '''
'''
        for ind in range(len(self.gcodes)):
            gcode = self.gcodes[ind]
            positions = self.positions[ind]
            for piece in gcode:
                self.grid += piece
            self.grid += box
            for b in positions:
                if b == "Bull":
                    pos = "✅"
                elif b == "Cow":
                    pos = "☑️"
                elif b == "Dead":
                    pos = "❌"
                self.grid += pos
            self.grid += '''
'''
        rem_rows = 8-len(self.gcodes)
        for row in range(rem_rows):
            self.grid += circle*4 + box + box_inv*4
            self.grid += '''
'''

    def colourify(self, nums, h):
        self.gcode = []
        if h == 0:
            for num in nums:
                self.gcode.append(self.colour_list[num])
            self.gcodes.append(self.gcode)
        else:
            for num in nums:
                self.hcode.append(self.colour_list[num])

    def guess(self, nums):
        self.colourify(nums, 0)
        self.pos = []
        gcode_temp = self.gcode.copy()
        hcode_temp = self.hcode.copy()
        for ind in range(len(self.hcode)):
            colour = self.hcode[ind]
            if colour == self.gcode[ind]:
                self.pos.append("Bull")
                gcode_temp.pop(ind - (4-len(gcode_temp)))
                hcode_temp.pop(ind - (4-len(hcode_temp)))
        for x in hcode_temp:
            if x in gcode_temp:
                self.pos.append("Cow")
                gcode_temp.remove(x)
            else:
                self.pos.append("Dead")
        rd.shuffle(self.pos)
        self.positions.append(self.pos)
        if self.gcode == self.hcode:
            self.game = 1
            self.winner = self.p2
        else:
            self.turns += 1