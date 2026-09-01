import json
import pandas as pd
from pathlib import Path

xlsx_path = Path.cwd().joinpath("input", "xlsx")
save_path = Path.cwd().joinpath("input", "json", "draft")

def deal_broker_check():
    for file_xlsx in xlsx_path.iterdir():
        if file_xlsx.suffix != ".xlsx":
            continue
        player_sheet = pd.read_excel(file_xlsx, sheet_name="Draft", skiprows=[16,32],
                                   usecols=[0,1,2,3], header = 0)
        deck_sheet = pd.read_excel(file_xlsx, sheet_name = "Play")

        for col in deck_sheet.columns:
            for card in deck_sheet[col].dropna():
                if "Snow-Covered" in card:
                    continue
                if card not in player_sheet[col].values:
                    print(f"{file_xlsx.stem} - {col} - {card}")


def xlsx_to_json():
    for file_xlsx in xlsx_path.iterdir():
        if file_xlsx.suffix != ".xlsx":
            continue
        file_num = file_xlsx.stem
        file_json = Path.joinpath(save_path, f"{file_num}.json")
        if file_json.exists():
            print(f"{str(file_json)} already exists.")
            continue

        pack_sheet = pd.read_excel(file_xlsx, sheet_name="Draft", skiprows=[16,32],
                                   usecols=[5,6,7,8], header = 0)
        deck_sheet = pd.read_excel(file_xlsx, sheet_name = "Play")

        #print(deck_sheet.shape)
        for col in deck_sheet.columns:
            if deck_sheet[col].dropna().size != 40:
                print(f"{file_num} - {col} ")






if __name__ == "__main__":
    deal_broker_check()