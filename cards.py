import math
import json
import helper
from pathlib import Path
from helper import get_oracle_path

raw_path = Path.cwd().joinpath("output", "raw.json")
list_path = Path.cwd().joinpath("output", "card_list.json")
oracle_path = get_oracle_path()
exception_path = Path.cwd().joinpath("input", "json", "mana_exceptions.json")

def generate_list():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with oracle_path.open("r", encoding="utf-8") as f:
        oracle_data = json.load(f)
    with exception_path.open("r", encoding="utf-8") as f:
        exception_data = json.load(f)
    unique_cards = set()
    for draft in raw_data:
        for pack in draft["packs"]:
            for card in pack["cards"]:
                unique_cards.add(card)
    for basic in exception_data["basics"]:
        unique_cards.add(basic)
        
    def card_list_entry(card_name):
        card_entry = [entry for entry in oracle_data if entry['name'] == card_name and
                    entry["object"] == "card" and entry["layout"] != "token"]
        card_dict = {}
        # special cases (ex. Lingering Souls) are in input/json/mana_exceptions.json
        if card_name in exception_data["exceptions"]:
            card_dict["mana"] = exception_data["exceptions"][card_name]["mana"]
        else:
            half_mana_string = ""
            # for multiple entries in Scryfall data, fix / add to exceptions immediately
            if len(card_entry) != 1: 
                print(f"Multiple oracle entries for {card_name}")
                mana_string = None
            # handling for multiface cards
            elif "card_faces" in card_entry[0]:
                type_lines = [d["type_line"] for d in card_entry[0]["card_faces"]]
                # filters out all non-mana faces (uncastable flips, lands)
                mana_cost_faces = [face for face in card_entry[0]["card_faces"] if face["mana_cost"] != ""]
                # multiple faces, count as half pips per side
                if any("Land" in w for w in type_lines) or len(mana_cost_faces) > 1:
                    half_mana_string = "".join(m["mana_cost"] for m in mana_cost_faces).lower()
                
                if len(mana_cost_faces) >= 1:
                    mana_string = mana_cost_faces[0]["mana_cost"]
                else:
                    mana_string = ""
            # normal handling
            else:
                mana_string = card_entry[0]["mana_cost"]
            def translate_mana_cost(mana_string):
                # TODO: check for if card faces are lands or adventures
                pips, splash = {}, {}
                if not mana_string:
                    return splash, pips
                # update when more colorless pips are introduced
                colorless_symbols = {"C", "X", "S"}
                symbols = mana_string.replace("{", "").split("}")
                splash_value = 1
                for s in symbols:
                    # skip colorless pips
                    if(not s or s.isnumeric() or s.upper() in colorless_symbols):
                        continue
                    # process colorless as half pips, including phyrexian mana
                    if("/" in s):
                        splash_value = 0.5
                        split_hybrid = s.split("/")
                        if "P" in split_hybrid:
                            split_hybrid.remove("P")
                        for c in split_hybrid:
                            pips[c] = pips.get(c, 0) + 0.5
                    # lowercase is set in mana_string for double face mana costs
                    elif s.islower():
                        pips[s.upper()] = pips.get(s.upper(), 0) + 0.5
                    else:
                        pips[s] = pips.get(s, 0) + 1
                for p in pips:
                    splash[p] = splash.get(p, 0) + splash_value
                return splash, pips

            if half_mana_string:
                splash, pips = translate_mana_cost(half_mana_string)
            else:
                splash, pips = translate_mana_cost(mana_string)
            color_profile = {"mana_cost" : mana_string,
                            "splash" : splash,
                            "pips" : pips}
            if "produced_mana" in card_entry[0]:
                color_profile["produced_mana"] = card_entry[0]["produced_mana"]
            card_dict["mana"] = color_profile
        
        if "image_uris" in card_entry[0]:
            img_url = card_entry[0]["image_uris"]["png"]
        elif "card_faces" in card_entry[0]:
            img_url = card_entry[0]["card_faces"][0]["image_uris"]["png"]
    
        card_dict.update({"tags": [], "img_url" : img_url})
        alias = helper.card_alias(card)
        if alias:
            card_dict["alias"] = alias
        return card_dict

    card_list = {}
    for card in unique_cards:
        card_list[card] = card_list_entry(card)
    card_list = dict(sorted(card_list.items()))
    with list_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(card_list, indent=4))

def generate_cards():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with list_path.open("r", encoding="utf-8") as f:
        card_list = json.load(f)

    for card in card_list:
        output = {"name" : card,
                  "picks" : []}
        # draft number , pick number, player , run or not, wins vs  
        for draft in raw_data:
            for player in draft["players"]:
                if card in player["pick_order"]:
                    pick_index = player["pick_order"].index(card)
                    pick_number = (pick_index % 15) + 1
                    pack_number = math.ceil(pick_index / 15)
                    run = card in player["decklist"]
                    #TODO: figure out wins vs players 
                    record = []
                    output["picks"].append({"draft_number" : draft["draft_number"],
                                            "player" : player["name"],
                                            "pack_number" : pack_number,
                                            "pick_number" : pick_number,
                                            "run" : run})
                    break
        card_name = card_list[card]["alias"] if "alias" in card_list[card] else card
        card_path = Path.cwd().joinpath("output", "cards", f"{card_name}.json")
        with card_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(output, indent=4))
                    
if __name__ == "__main__":
    generate_cards()