import os
import json
import requests
from time import sleep
from pathlib import Path

from helper import get_oracle_path

raw_path = Path.cwd().joinpath("output", "raw.json")
list_path = Path.cwd().joinpath("output", "card_list.json")
oracle_path = get_oracle_path()

def assign_colors(data, card_name):
    return [entry for entry in data if entry['name'] == card_name and
            entry["object"] == "card" and entry["layout"] != "token"]


def generate_list():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    unique_cards = set()
    for draft in raw_data:
        for pack in draft["packs"]:
            for card in pack["cards"]:
                unique_cards.add(card)
    
    with oracle_path.open("r", encoding="utf-8") as f:
        oracle_data = json.load(f)
    
    card_dict = {}
    for card in unique_cards:
        temp_dict = {}
        temp_dict["mana_cost"] = assign_colors(oracle_data, card)
        card_dict[card] = temp_dict
    card_dict = dict(sorted(card_dict.items()))

    with list_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(card_dict, indent=4))

#generate_list()


def generate_cards():
    card_list = open(os.path.join(os.getcwd(), 'card_list.json'))
    card_list_data = json.load(card_list)
    
    raw = open(os.path.join(os.getcwd(), 'raw.json'))
    data = json.load(raw)
    
    for card in card_list_data:
        output = {"name" : card}

    
    card_list.close()