import openpyxl
from openpyxl import styles
import os

save_path = os.path.dirname(f"{os.getcwd()}/archive/")

draft_num = input("Enter draft number: ")
#draft_date = input("Enter draft date (MM/DD/YYYY): ")
#draft_patch = input("Enter patch number: ")

with open(f"{save_path}/input/player_results.txt",
          'r', encoding="utf-8") as result:
    player_file = result.read().split('\n')
with open(f"{save_path}/input/pack_results.txt",
          'r', encoding="utf-8") as result:
    pack_file = result.read().split('\n')

wb = openpyxl.Workbook()
base_style = styles.NamedStyle(name="base",
                               font=styles.Font(name="Cambria",
                                                size=12),
                                alignment=styles.Alignment(horizontal="center"))
draft_sheet = wb.active
draft_sheet.title = ("Draft")
color_order = {"Green" : [0, "ff78d05c"], "Blue" : [1, "ff6FBBEA"],
               "Red" : [2, "ffEA6F6F"], "Purple" : [3, "ffAE6FEA"]}

class Player:
    def __init__(self, data):
        self.name, self.color = data.pop(0).split('-#-')
        self.packs = {}
        for idx, line in enumerate(data):
            self.packs[line] = idx
    def __lt__(self, other):
        return(color_order[self.color][0] < color_order[other.color][0])
        
def write_cell(sheet, row, col, value, color):
    curr_cell = sheet.cell(row=row, column=col)
    curr_cell.value = value
    curr_cell.style = base_style
    curr_cell.fill = styles.PatternFill(start_color=color_order[color][1],
                                        fill_type="solid")

players = []
lines = []
for line in player_file:
    if "#413" in line:
        players.append(Player(lines))
        lines.clear()
    else:
        lines.append(line)
players = sorted(players)
row = 1
col = 1
for p in players:
    write_cell(draft_sheet, row, col, p.name, p.color)
    write_cell(draft_sheet, row, col + 5, p.name, p.color)
    for card, index in p.packs.items():
        if row - 1 % 15 == 0:
            row += 2
        else:
            row += 1
        write_cell(draft_sheet, row, col, card, p.color)
    col += 1
    row = 1

class DraftCard:
    def __init__(self, name, pick_num, color, player_num):
        self.name = name
        self.pick_num = pick_num
        self.color = color
        self.player_num = player_num
    def __lt__(self, other):
        return(self.pick_num < other.pick_num)

def find_card_player(card_name):
    for p_index, p_value in enumerate(players):
        for c_key, c_value in p_value.packs.items():
                if card_name == c_key:
                    return(DraftCard(card_name, c_value,
                                     p_value.color, p_index))
    return None

def find_player_col(pack):
    for col in range(len(players)):
        if pack[0].color == players[col].color:
            return(col + 6)
    return(-1)

row = 2
counter = 0
temp_pack = []
for line in pack_file:
    if "#413" in line:
        temp_pack.sort()
        col = find_player_col(temp_pack)
        for card in temp_pack:
            write_cell(draft_sheet, row + card.pick_num, col,
                       card.name, card.color)
            counter += 1
            if counter % 60 == 0:
                row += 1 
        temp_pack.clear()
    else:
        temp_card = find_card_player(line)
        if temp_card is None:
            print("Not Found")
        else:
            temp_pack.append(temp_card)

class DeckCard:
    def __init__(self, name, cmc, qty):
        self.name = name
        self.cmc = cmc
        self.qty = qty
    def __lt__(self, other):
        if self.cmc != other.cmc:
            return self.cmc < other.cmc
        else:
            return self.name < other.name
        
def write_deck(deck, col):
    cards = []
    row = 0
    curr_color = color_order[deck[0]]
    
        


wb.save(f"{os.getcwd()}/{draft_num}.xlsx")