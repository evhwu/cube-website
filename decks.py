import json
from pathlib import Path
import helper
import copy

raw_path = Path.cwd().joinpath("output", "raw.json")
card_list_path = Path.cwd().joinpath("output", "card_list.json")

#def deck_name(pips, splash):



def update_raw_colors():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with card_list_path.open("r", encoding="utf-8") as f:
        card_list_data = json.load(f)
    raw_rewrite = copy.deepcopy(raw_data)

    for draft_i, draft in enumerate(raw_data):
        for player_i, player in enumerate(draft["players"]):
            pips, splash = {}, {}
            for card in player["decklist"]:
                #alias = helper.card_alias(card)
                #card_name = alias if alias is not None else card
                if card not in card_list_data:
                    print(card)
                    continue
                card_dict = card_list_data[card]

                for key, value in card_dict["mana"]["pips"].items():
                    pips[key] = pips.get(key, 0) + value
                for key, value in card_dict["mana"]["splash"].items():
                    splash[key] = splash.get(key, 0) + value
            current_deck = raw_rewrite[draft_i]["players"][player_i]
            current_deck["pips"] = pips
            current_deck["splash"] = splash
            #current_deck["deck_name"] = deck_name(pips, splash)
    

    print("hehe")




        
    
    

if __name__ == "__main__":
    update_raw_colors()