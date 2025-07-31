import openpyxl
import os

save_path = os.path.dirname(f"{os.getcwd()}/archive/")

with open(f"{save_path}/input/player_results.txt", 'r', encoding="utf-8") as result:
    player_file = result.read().split('\n')
with open(f"{save_path}/input/pack_results.txt", 'r', encoding="utf-8") as result:
    pack_file = result.read().split('\n')

wb = openpyxl.Workbook()

draft_num = input("Enter draft number: ")
draft_date = input("Enter draft date (MM/DD/YYYY): ")
draft_patch = input("Enter patch number: ")

base_style = openpyxl.NamedStyle(name="base",
                                 font=openpyxl.Font(name="Cambria", size=12),
                                 alignment=openpyxl.Alignment(horizontal="center"))

draft_sheet = wb.create_sheet(title="Draft")
color_order = {"Green" : 0,"Blue" : 1,"Red" : 2,"Purple" :3}

players = []

class Player:
    def __init__(self, data):
        self.name, self.color = data.pop(0).split('-#-')
        self.packs = [[]]
        
        for line in data:
            if len(self.packs[len(self.packs)-1]) == 15:
                self.packs.append([])
            self.packs[len(self.packs)-1].append(line)
    
    def __lt__(self, other):
        return(color_order[self.color] < color_order[other.color])

lines = []
for line in player_file:
    if "#413" in line:
        players.append(Player(lines))
        lines.clear()
    else:
        lines.append(line)

players = sorted(players)

curr_row, curr_col = 0
for p in players:
    draft_sheet.
    
        
        
        
wb.save(f"{os.getcwd()}/{draft_num}.xlsx")