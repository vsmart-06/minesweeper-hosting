import random as rd

class uno:
    def __init__(self, theme = "dark", uno_cards = []):
        self.cards = []
        self.cards_string = ""
        self.opt_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "skip", "reverse", "+2", "+4", "wild"]
        self.colours = ["red", "green", "blue", "yellow"]
        self.colour_emojis = {"red": "🟥", "green": "🟩", "blue": "🟦", "yellow": "🟨"}
        self.card_dict = {(0, "red"): uno_cards[0], (0, "green"): uno_cards[1], (0, "blue"): uno_cards[2], (0, "yellow"): uno_cards[3], (1, "red"): uno_cards[4], (1, "green"): uno_cards[5], (1, "blue"): uno_cards[6], (1, "yellow"): uno_cards[7], (2, "red"): uno_cards[8], (2, "green"): uno_cards[9], (2, "blue"): uno_cards[10], (2, "yellow"): uno_cards[11], (3, "red"): uno_cards[12], (3, "green"): uno_cards[13], (3, "blue"): uno_cards[14], (3, "yellow"): uno_cards[15], (4, "red"): uno_cards[16], (4, "green"): uno_cards[17], (4, "blue"): uno_cards[18], (4, "yellow"): uno_cards[19], (5, "red"): uno_cards[20], (5, "green"): uno_cards[21], (5, "blue"): uno_cards[22], (5, "yellow"): uno_cards[23], (6, "red"): uno_cards[24], (6, "green"): uno_cards[25], (6, "blue"): uno_cards[26], (6, "yellow"): uno_cards[27], (7, "red"): uno_cards[28], (7, "green"): uno_cards[29], (7, "blue"): uno_cards[30], (7, "yellow"): uno_cards[31], (8, "red"): uno_cards[32], (8, "green"): uno_cards[33], (8, "blue"): uno_cards[34], (8, "yellow"): uno_cards[35], (9, "red"): uno_cards[36], (9, "green"): uno_cards[37], (9, "blue"): uno_cards[38], (9, "yellow"): uno_cards[39], ("skip", "red"): uno_cards[40], ("skip", "green"): uno_cards[41], ("skip", "blue"): uno_cards[42], ("skip", "yellow"): uno_cards[43], ("reverse", "red"): uno_cards[44], ("reverse", "green"): uno_cards[45], ("reverse", "blue"): uno_cards[46], ("reverse", "yellow"): uno_cards[47], ("+2", "red"): uno_cards[48], ("+2", "green"): uno_cards[49], ("+2", "blue"): uno_cards[50], ("+2", "yellow"): uno_cards[51], ("+4", "colourful"): uno_cards[52], ("wild", "colourful"): uno_cards[53]}

        for x in range(7):
            num = rd.choice(self.opt_cards)
            if num not in ["+4", "wild"]:
                colour = rd.choice(self.colours)
                self.cards.append((num, colour))
            else:
                self.cards.append((num, "colourful"))
        if theme == "dark":
            self.box = "⬛"
        else:
            self.box = "⬜"
    
    def colour_card(self, card):
        try:
            card_string = self.card_dict[card]
        except KeyError:
            card_string = f'{self.card_dict[(card[0], "colourful")]} {self.colour_emojis[card[1]]}'
        return card_string

    def string_rows(self):
        self.cards_string = ""
        for x in self.cards:
            self.cards_string += f"{self.card_dict[x]} "

    def available_card(self, top_card):
        number = top_card[0]
        colour = top_card[1]
        has_card = False
        colour_in = False
        for card in self.cards:
            if card[1] == colour:
                colour_in = True
                break
        for card in self.cards:
            if card[0] == number or card[1] == colour or card[1] == "colourful":
                if not(card == ("+4", "colourful") and colour_in):
                    has_card = True
                    break
        return has_card
    
    def choose_card(self, top_card, choice):
        number_1 = top_card[0]
        colour_1 = top_card[1]
        card = self.cards[choice-1]
        number_2 = card[0]
        colour_2 = card[1]
        valid_card = False
        colour_in = False
        game_over = False
        for c in self.cards:
            if c[1] == colour_1:
                colour_in = True
                break
        if number_1 == number_2 or colour_1 == colour_2 or colour_2 == "colourful":
            if not(card == ("+4", "colourful") and colour_in):
                valid_card = True
        if valid_card:
            self.cards.remove(card)
            if self.cards == []:
                game_over = True
        return valid_card, card, game_over
    
    def draw(self, draw_num):
        for x in range(draw_num):
            num = rd.choice(self.opt_cards)
            if num not in ["+4", "wild"]:
                colour = rd.choice(self.colours)
                self.cards.append((num, colour))
            else:
                self.cards.append((num, "colourful"))