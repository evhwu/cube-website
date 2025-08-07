import os
import json
import pandas as pd
save_path = os.path.dirname(f"{os.getcwd()}/input/")

def generate_json():
    input_files = os.listdir(save_path)
    draft_records = []

    for f in input_files:
        file_num, file_ext = os.path_splitext(f)
        file_name = os.path.join(save_path, f)
        if file_ext != ".xlsx":
            continue

        date_sheet = pd.read_excel(file_name, sheet_name = "Date", header = None)
        match_sheet = pd.read_excel(file_name, sheet_name = "Results",
                                    usecols = [0,1,2])
        matches = []
        def write_match_row(row):
            loser = row["Player 1"] if row["Winner"] == row["Player 2"] else row["Player 2"]
            matches.append({"winner" : row["Winner"], "loser" : loser})
        



        draft = {"draft_number" : file_num, "date" : date_sheet.iloc[0,0],
                 "patch" : date_sheet.iloc[1,0], "matches" : matches}
        