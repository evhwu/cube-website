import openpyxl
from openpyxl import styles
import os
import requests
from time import sleep
save_path = os.path.dirname(f"{os.getcwd()}/input/")

# Records draft from Tabletop Simulator. Read from input/text/ deck, pack, player results
def record_xlsx(): 
    with open(f"{save_path}/text/player_results.txt",
            'r', encoding="utf-8") as result:
        player_file = result.read().split('\n')
    with open(f"{save_path}/text/pack_results.txt",
            'r', encoding="utf-8") as result:
        pack_file = result.read().split('\n')
    with open(f"{save_path}/text/deck_results.txt",
            'r', encoding="utf-8") as result:
        deck_file = result.read().split('\n')

    # Checks each line in the pack file. 1 includes all potential misspellings, including autocorrected ones.
    confirm = int(input("Check for misspellings? 1 - All, 2 - Ignore Short, 3 - Skip: "))
    if confirm != 3:
        for line in pack_file:
            request_string = f"https://api.scryfall.com/cards/search?q={line}"
            response = requests.get(request_string,
                                    params = {"format" : "json"})
            try:
                card_dict = response.json()["data"]
                for card_entry in card_dict:
                    if line != card_entry['name'] and confirm == 1:
                        print(f"{line} -- {card_entry['name']}")
            except:
                if line != "#413":
                    print(line)
            sleep(0.125)

    wb = openpyxl.Workbook()
    base_style = styles.NamedStyle(name="base",
                                font=styles.Font(name="Cambria",
                                                    size=12),
                                    alignment=styles.Alignment(horizontal="center"))

    def write_cell(sheet, row, col, value, color = None):
        curr_cell = sheet.cell(row=row, column=col)
        curr_cell.value = value
        curr_cell.style = base_style
        if color:
            curr_cell.fill = styles.PatternFill(start_color=color_order[color][1],
                                                fill_type="solid")

    draft_sheet = wb.active
    draft_sheet.title = "Draft" 
    color_order = {"Green" : [0, "ff78d05c"], "Blue" : [1, "ff6FBBEA"],
                "Red" : [2, "ffEA6F6F"], "Purple" : [3, "ffAE6FEA"]}
    deck_sheet = wb.create_sheet(title = "Play")

    class Player:
        def __init__(self, data):
            self.name, self.color = data.pop(0).split('-#-')
            self.packs = {}
            for idx, line in enumerate(data):
                self.packs[line] = idx
        def __lt__(self, other):
            return(color_order[self.color][0] < color_order[other.color][0])

    #Creates the player list from player file. Players_dict is used in results_sheet later.
    players = []
    lines = []
    for line in player_file:
        if "#413" in line:
            players.append(Player(lines))
            lines.clear()
        else:
            lines.append(line)
    players = sorted(players)
    players_dict = {}
    for p in players:
        players_dict[p.name] = p

    draft_num = input("Enter draft number: ")
    draft_date = input("Enter draft date (MM/DD/YYYY): ")
    draft_patch = input("Enter patch number: ")

    #Creates results sheets. Ranking is based on number of wins, so make sure to enter input correctly.
    result_sheet = wb.create_sheet(title = "Results")
    write_cell(result_sheet, 1, 1, "Player 1")
    write_cell(result_sheet, 1, 2, "Player 2")
    write_cell(result_sheet, 1, 3, "Winner")
    write_cell(result_sheet, 1, 5, "Ranking")
    row = 2
    player_wins = {}
    for index, p in enumerate(players):
        player_wins[index] = [p, 0]
        print(f"{index} - {p.name}")
    while row <= 7:
        w_index = int(input("Enter winner of round: "))
        l_index = int(input("Enter loser of round: "))
        write_cell(result_sheet, row, 1,
                player_wins[w_index][0].name, player_wins[w_index][0].color)
        write_cell(result_sheet, row, 2,
                player_wins[l_index][0].name, player_wins[l_index][0].color)
        write_cell(result_sheet, row, 3,
                player_wins[w_index][0].name, player_wins[w_index][0].color)
        player_wins[w_index][1] = player_wins[w_index][1] + 1
        row += 1
    for index, p in player_wins.items():
            write_cell(result_sheet, 5-p[1], 5, p[0].name, p[0].color)

    #Writes the player titles and the player pick order in the draft sheet
    row = 1
    col = 1
    for p in players:
        write_cell(draft_sheet, row, col, p.name, p.color)
        write_cell(draft_sheet, row, col + 5, p.name, p.color)
        row += 1
        for card, index in p.packs.items():
            write_cell(draft_sheet, row, col, card, p.color)
            row += 1
            if row == 17 or row == 33:
                row += 1
        col += 1
        row = 1

    #Patch and date info
    date_sheet = wb.create_sheet(title = "Date")
    write_cell(date_sheet, 1, 1, draft_date)
    write_cell(date_sheet, 2, 1, draft_patch)

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

    #Writes the right side of the draft sheet by matching to pick order in player list
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

    # Writes from deck results file. Used scryfall request to sort by cmc. Make sure to check for misspellings, or decklists may be imcomplete.
    def write_deck(deck, col):
        cards = []
        for p in players:
            if p.name == deck[0]:
                color = p.color
        write_cell(deck_sheet, 1, col, deck.pop(0), color)
        row = 2
        for line in deck:
            found = False
            for c in cards:
                if c.name == line:
                    c.qty += 1
                    found = True
                    break
            if found:
                continue
            request_string = f"https://api.scryfall.com/cards/search?q={line}"
            response = requests.get(request_string,
                                    params = {"format" : "json"})
            card_dict = response.json()["data"]
            for card_entry in card_dict:
                if card_entry["name"] == line:
                    temp_cmc = card_entry["cmc"]
                    cards.append(DeckCard(line, temp_cmc, 1))
                    break
            sleep(0.125)
        cards = sorted(cards)
        for c in cards:
            for q in range(c.qty):
                write_cell(deck_sheet, row, col, c.name, color)
                row += 1

    #Sorts decks by player color before writing.
    curr_deck = []
    decks = []
    for line in deck_file:
        if "#413" == line:
            decks.append(curr_deck)
            curr_deck = []
        else:
            curr_deck.append(line)
    decks.sort(key = lambda d: players_dict[d[0]])
    col = 1
    for d in decks:
        write_deck(d, col)
        col += 1
    wb.save(f"{os.getcwd()}/{draft_num}.xlsx")

if __name__ == "__main__":
    record_xlsx()