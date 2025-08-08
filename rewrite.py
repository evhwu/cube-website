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

        #TODO: rewrite the row 2 swap - so that loser's 3/4 always played first
        for index, row in match_sheet.iterrows():
            if index == 2:
                if row["Player 1"] == lastrow["Winner"] or row["Player 2"] == lastrow["Winner"]:
                    is_swap = True
                else:
                    write_match_row(row)
            elif is_swap:
                write_match_row(row)
                write_match_row(lastrow)
                is_swap = False
            else:
                write_match_row(row)
            lastrow = row
        #end
        draft = {"draft_number" : file_num, "date" : date_sheet.iloc[0,0],
                 "patch" : date_sheet.iloc[1,0], "matches" : matches,
                 "packs" : [], "players" : []}
        pack_sheet = pd.read_excel(file_name, sheet_name="Draft",
                                   skiprows=[16,32], usecols=[5,6,7,8],
                                   header=0)
        for series_name, series in pack_sheet.items():
            packs = series.to_list()
            for i in range(3):
                draft["packs"].append({"player" : series_name.removesuffix(".1"),
                                       "number" : i + 1,
                                       "cards" : packs[i*15:((i + 1) * 15)]})
        rank_sheet = pd.read_excel(file_name, sheet_name = "Results",
                                   usecols = [4], skiprows = [5,6])
        player_sheet = pd.read_excel(file_name, sheet_name = "Draft",
                                     skiprows = [16,32], usecols = [0,1,2,3],
                                     header = 0)
        deck_sheet = pd.read_excel(file_name, sheet_name = "Play").dropna()
        
        
        
