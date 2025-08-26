import os
import json
import pandas as pd
from pathlib import Path

# return path to oracle bulk file
def get_oracle_path():
    input_path = Path.cwd().joinpath("input", "json")
    for f in input_path.iterdir():
        if "oracle-cards" in f.name:
            return f
    return None

# find each occurence of card in xlsx
def find_xlsx_card(card_name):
    input_path = Path.cwd().joinpath("input", "xlsx")
    for f in input_path.iterdir():
        draft_sheet = pd.read_excel(f, sheet_name="Draft",
                                    skiprows=[16,32], header=0)
        for series_name, series in draft_sheet.items():
            if card_name in series.values:
                print(f"{f} - {series_name}")

# make aliases for double faced cards (windows OS dislikes //)
# shorten makes a long string into short, otherwise short to long
def card_alias(card_name, shorten=True):
    if shorten:
        if "//" in card_name:
            return card_name.split(" // ")[0]
        return None
    else:
        list_path = Path.cwd().joinpath("output", "card_list.json")
        with list_path.open("r", encoding="utf-8") as f:
            card_list = json.load(f)
        if "alias" in card_list[card_name] :
            return card_list[card_name]["alias"]
        return None
    
    