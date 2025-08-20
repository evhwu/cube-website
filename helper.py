import os
import pandas as pd
from pathlib import Path

#return path to oracle bulk file
def get_oracle_path():
    input_path = Path.cwd().joinpath("input", "json")
    for f in input_path.iterdir():
        if "oracle-cards" in f.name:
            return f
    return None

#find each occurence of card in xlsx
def find_xlsx_card(card_name):
    input_path = Path.cwd().joinpath("input", "xlsx")
    for f in input_path.iterdir():
        draft_sheet = pd.read_excel(f, sheet_name="Draft",
                                    skiprows=[16,32], header=0)
        for series_name, series in draft_sheet.items():
            if card_name in series.values:
                print(f"{f} - {series_name}")
