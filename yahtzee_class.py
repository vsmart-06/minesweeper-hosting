import random as rd

class yahtzee:
    def __init__(self, user_id, d1, d2, d3, d4, d5, d6):
        self.dice = []
        self.sdice = []
        self.scores = {"U1": None, "U2": None, "U3": None, "U4": None, "U5": None, "U6": None, "L1": None, "L2": None, "L3": None, "L4": None, "L5": None, "L6": None, "L7": None}
        self.total = 0
        self.utotal = 0
        self.ltotal = 0
        self.bonus = 0
        self.rolls = 3
        self.empty_pos = 13
        self.left = ""
        self.middle = ""
        self.right = ""
        self.sdice = []
        self.joker = False
        self.joker_num = 0
        self.utotal_bonus = False
        self.game = 0
        self.user_id = user_id
        self.invalid = 0
        self.counts = {}
        self.quit = 0
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5
        self.d6 = d6
    
    def string_dice(self):
        self.sdice = []
        for die in self.dice:
            if die == 1:
                self.sdice.append(self.d1)
            elif die == 2:
                self.sdice.append(self.d2)
            elif die == 3:
                self.sdice.append(self.d3)
            elif die == 4:
                self.sdice.append(self.d4)
            elif die == 5:
                self.sdice.append(self.d5)
            elif die == 6:
                self.sdice.append(self.d6)

    def string_rows(self):
        self.left = ""
        self.middle = ""
        self.right = ""
        for x in self.scores:
            if x == "U1":
                self.left += "`U1`. *Aces*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "U2":
                self.left += "`U2`. *Twos*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "U3":
                self.left += "`U3`. *Threes*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "U4":
                self.left += "`U4`. *Fours*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "U5":
                self.left += "`U5`. *Fives*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "U6":
                self.left += "`U6`. *Sixes*: "
                self.left += f"**{self.scores[x]}**"
                self.left += '''
'''
            elif x == "L1":
                self.middle += "`L1`. *3 in a row*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L2":
                self.middle += "`L2`. *4 in a row*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L3":
                self.middle += "`L3`. *Full house*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L4":
                self.middle += "`L4`. *Small straight*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L5":
                self.middle += "`L5`. *Large straight*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L6":
                self.middle += "`L6`. *Yahtzee*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
            elif x == "L7":
                self.middle += "`L7`. *Chance*: "
                self.middle += f"**{self.scores[x]}**"
                self.middle += '''
'''
        self.right += f'''*Upper total*: **{self.utotal}**
*Lower total*: **{self.ltotal}**
*Bonus*: **{self.bonus}**
***Total score***: **{self.total}**
'''

    def roll(self):
        self.counts = {}
        self.dice = self.sdice.copy()
        for x in range(5-len(self.sdice)):
            self.dice.append(rd.randint(1, 6))
        for x in range(1, 7):
            self.counts[x] = self.dice.count(x)
        self.sdice = []
        self.rolls -= 1

    def store(self, nums):
        self.sdice = nums
        self.dice = []
    
    def points(self, loc):
        loc = str(loc)
        if self.scores[loc] == None:
            for count in self.counts:
                if self.counts[count] == 5 and self.scores["L6"] == 50:
                    self.bonus += 100
                    self.total += 100
                    self.joker = True
                    self.joker_num = count
                    break
                elif self.counts[count] == 5 and self.scores["L6"] == 0:
                    self.joker = True
                    self.joker_num = count
                    break
            if loc.startswith("U"):
                num = int(loc[1])
                self.scores[loc] = self.counts[num]*num
                self.utotal += self.counts[num]*num
                self.total += self.counts[num]*num
                if self.utotal >= 63 and not(self.utotal_bonus):
                    self.bonus += 35
                    self.total += 35
                    self.utotal_bonus = True

            else:
                num = int(loc[1])
                total = 0
                if num == 1:
                    for count in self.counts:
                        if self.counts[count] >= 3:
                            total = sum(self.dice)
                            break
                elif num == 2:
                    for count in self.counts:
                        if self.counts[count] >= 4:
                            total = sum(self.dice)
                            break
                elif num == 3:
                    if not(self.joker):
                        twofer = False
                        threefer = False
                        for count in self.counts:
                            if self.counts[count] == 3:
                                threefer = True
                            elif self.counts[count] == 2:
                                twofer = True
                        if twofer and threefer:
                            total = 25
                    else:
                        if self.scores[f"U{self.joker_num}"] != None:
                            total = 25
                        else:
                            total = 0
                        self.joker = False
                elif num == 4:
                    if not(self.joker):
                        sstraight = False
                        for x in range(1, 4):
                            if self.counts[x] > 0 and self.counts[x+1] > 0 and self.counts[x+2] > 0 and self.counts[x+3] > 0:
                                sstraight = True
                                break
                        if sstraight:
                            total = 30
                    else:
                        if self.scores[f"U{self.joker_num}"] != None:
                            total = 30
                        else:
                            total = 0
                        self.joker = False
                elif num == 5:
                    if not(self.joker):
                        lstraight = False
                        for x in range(1, 3):
                            if self.counts[x] > 0 and self.counts[x+1] > 0 and self.counts[x+2] > 0 and self.counts[x+3] > 0 and self.counts[x+4]:
                                lstraight = True
                                break
                        if lstraight:
                            total = 40
                    else:
                        if self.scores[f"U{self.joker_num}"] != None:
                            total = 40
                        else:
                            total = 0
                        self.joker = False
                elif num == 6:
                    for count in self.counts:
                        if self.counts[count] == 5:
                            total = 50
                            break
                elif num == 7:
                    total = sum(self.dice)
                self.scores[loc] = total
                self.ltotal += total
                self.total += total
            
            self.empty_pos -= 1
            self.rolls = 3
            self.dice = []
            self.sdice = []
            self.invalid = 0
            
        else:
            self.invalid = 1

'''game = yahtzee()
while game.empty_pos > 0:
    game.string_rows()
    print(game.card)
    inp = ""
    while game.rolls > 0 and inp != "stop":
        game.roll()
        print(game.dice)
        if game.rolls > 0:
            inp = input("Enter which dice you would like to hold: ")
            inp = inp.lower()
            if inp != "stop":
                nums = list(map(int, inp.split()))
                if nums[0] != 0:
                    game.store(nums)
    game.string_rows()
    print(game.card)
    loc = input("Where would you like to put your points in: ")
    loc = loc.upper()
    game.points(loc)
game.string_rows()
print(game.card)
print(f"Your final score is: {game.total}")'''