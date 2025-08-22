import os
import json
import requests
from time import sleep
from pathlib import Path
from helper import get_oracle_path

raw_path = Path.cwd().joinpath("output", "raw.json")
list_path = Path.cwd().joinpath("output", "card_list.json")
oracle_path = get_oracle_path()



def translate_mana_cost(mana_string):
    if not mana_string:
        return "", ""
    colorless_symbols = {"C", "X", "S"}
    symbols = mana_string.replace("{", "").split("}")
    pips = {}

    for s in symbols:
        if(not s or s.isnumeric() or s in colorless_symbols):
            continue
        if("/" in s):
            split_hybrid = s.split("/")
            if "P" in split_hybrid:
                split_hybrid.remove("P")
            for c in split_hybrid:
                pips[c] = pips.get(c, 0) + 0.5
        elif s.islower():
            pips[s.upper()] = pips.get(s, 0) + 0.5
        else:
            pips[s] = pips.get(s, 0) + 1



    return "", pips

    
        
def assign_colors(data, card_name):
    card_entry =  [entry for entry in data if entry['name'] == card_name and
                   entry["object"] == "card" and entry["layout"] != "token"]
    if len(card_entry) != 1: 
        print(f"Multiple oracle entries for {card_name}")
        mana_string = None
    elif "card_faces" in card_entry[0]:
        mana_cost_faces = [face for face in card_entry[0]["card_faces"] if face["mana_cost"] != ""]
        if len(mana_cost_faces) == 1:
            mana_string = mana_cost_faces[0]["mana_cost"]
        else:
            mana_string = "".join(m["mana_cost"] for m in mana_cost_faces).lower()
            print(f"{card_name} - {mana_string}")
    else:
        mana_string = card_entry[0]["mana_cost"]

    splash, pips = translate_mana_cost(mana_string)
    color_profile = {"mana_cost" : mana_string,
                     "splash" : splash,
                     "pips" : pips}
    return color_profile
    # need mana cost for curve + color curve
    # number of mana cards for splash
    # number of pips for colors


        

def generate_list():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with oracle_path.open("r", encoding="utf-8") as f:
        oracle_data = json.load(f)
    unique_cards = set()
    for draft in raw_data:
        for pack in draft["packs"]:
            for card in pack["cards"]:
                unique_cards.add(card)

    card_dict = {}
    for card in unique_cards:
        temp_dict = {"mana_cost" : assign_colors(oracle_data, card),
                     "tags" : []}
        card_dict[card] = temp_dict
    card_dict = dict(sorted(card_dict.items()))
    with list_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(card_dict, indent=4))

def generate_cards():
    card_list = open(os.path.join(os.getcwd(), 'card_list.json'))
    card_list_data = json.load(card_list)
    
    raw = open(os.path.join(os.getcwd(), 'raw.json'))
    data = json.load(raw)
    
    for card in card_list_data:
        output = {"name" : card}

    
    card_list.close()

generate_list()