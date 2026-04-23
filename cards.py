import math
import json
import helper
from pathlib import Path
from helper import get_oracle_path

raw_path = Path.cwd().joinpath("output", "raw.json")
list_path = Path.cwd().joinpath("output", "card_list.json")
oracle_path = get_oracle_path()
exception_path = Path.cwd().joinpath("input", "json", "mana_exceptions.json")

def generate_cards():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    for card in raw_data["card_list"]:
        output = {"name" : card,
                  "picks" : []}
        # draft number , pick number, player , run or not, wins vs  
        for draft in raw_data["draft_records"]:
            for player in draft["players"]:
                if card in player["pick_order"]:
                    pick_index = player["pick_order"].index(card)
                    pick_number = (pick_index % 15) + 1
                    pack_number = math.ceil((pick_index+1) / 15)
                    run = card in player["decklist"]
                    #TODO: figure out wins vs players
                    #temp , using rank instead
                    rank = player["rank"] 
                    deck_name = player["deck_name"]
                    record = []
                    output["picks"].append({"draft_number" : draft["draft_number"],
                                            "player" : player["name"],
                                            "pack_number" : pack_number,
                                            "pick_number" : pick_number,
                                            "run" : run,
                                            "rank" : rank,
                                            "deck_name": deck_name})
                    break
        card_name = raw_data["card_list"][card]["alias"] if "alias" in raw_data["card_list"][card] else card
        card_path = Path.cwd().joinpath("output", "cards", f"{card_name}.json")
        with card_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(output, indent=4))
                    
if __name__ == "__main__":
    generate_cards()