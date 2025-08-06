import os
import pandas as pd
save_path = os.path.dirname(f"{os.getcwd()}/input/")

def find_card(card_name):
    archive_files = os.listdir(save_path)
    for f in archive_files:
        file_name = os.path.join(save_path, f)
        if("input" in file_name):
            continue
        draft_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                    header=0)
        for series_name, series in draft_sheet.items():
            for card in series:
                if card == card_name:
                    print(f"{f} - {series_name}")
