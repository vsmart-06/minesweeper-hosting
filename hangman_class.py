class hangman:
    def __init__(self):
        self.hword = ""
        self.gword = ""
        self.letters = []
        for x in range(97, 123):
            if chr(x) not in "aeiou":
                self.letters.append(chr(x))
        self.game = 0
        self.misses = 0
        self.letters_string = ""
    
    def sto_word(self, word):
        self.hword = word
        self.gword = ""
        for x in self.hword:
            if x != " " and x not in "aeiou":
                if self.gword == "" or self.gword[-1] == " ":
                    self.gword += "- "
                else:
                    self.gword += " - "
            else:
                if x == " ":
                    self.gword += "   "
                else:
                    self.gword += x
    
    def string_letters(self):
        self.letters_string = ""
        for x in range(97, 123):
            l = chr(x)
            if l in self.letters:
                self.letters_string += f"{l.upper()} " 
            else:
                self.letters_string += f"~~{l.upper()}~~ "
        self.letters_string = self.letters_string[0:-1]

    def guess(self, letter):
        in_word = False
        invalid = 0
        if letter in self.letters:
            self.letters.remove(letter)
            if letter in self.hword:
                in_word = True
                self.gword = ""
                for x in self.hword:
                    if x != " " and x in self.letters:
                        if self.gword == "" or self.gword[-1] == " ":
                            self.gword += "- "
                        else:
                            self.gword += " - "
                    else:
                        if x != " ":
                            self.gword += x
                        else:
                            self.gword += "   "
                if "-" not in self.gword:
                    self.game = 1
            else:
                self.misses += 1
            
        else:
            invalid = 1
        return in_word, invalid