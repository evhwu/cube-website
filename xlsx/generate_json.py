import os
import json
import pandas as pd
save_path = os.path.dirname(f"{os.getcwd()}/input/xlsx/")

def generate_json():
    input_files = os.listdir(save_path)
    draft_records = []

    for f in input_files:
        file_num, file_ext = os.path.splitext(f)
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
        swap = False 
        last_row = pd.Series()

        #TODO: rewrite the row 2 swap - so that loser's 3/4 always played first
        for index, row in match_sheet.iterrows():
            if index == 2:
                if row["Player 1"] == last_row["Winner"] or row["Player 2"] == last_row["Winner"]:
                    swap = True
                else:
                    write_match_row(row)
            elif swap:
                write_match_row(row)
                write_match_row(last_row)
                swap = False
            else:
                write_match_row(row)
            last_row = row
        
        draft = {"draft_number" : file_num, "date" : date_sheet.iloc[0,0],
                 "patch" : date_sheet.iloc[1,0], "matches" : matches,
                 "packs" : [], "players" : []}
        
        #writes the pack pick order
        pack_sheet = pd.read_excel(file_name, sheet_name="Draft",
                                   skiprows=[16,32], usecols=[5,6,7,8],
                                   header=0)
        seat_counter = 1
        seat_to_player = {}
        for series_name, series in pack_sheet.items():
            packs = series.to_list()
            for i in range(3):
                draft["packs"].append({"player" : series_name.removesuffix(".1"),
                                       "seat" : seat_counter,
                                       "number" : i + 1,
                                       "cards" : packs[i*15:((i + 1) * 15)]})
            seat_to_player[series_name.removesuffix(".1")] = seat_counter
            seat_counter += 1
        
        rank_sheet = pd.read_excel(file_name, sheet_name = "Results",
                                   usecols = [4], skiprows = [5,6])
        player_sheet = pd.read_excel(file_name, sheet_name = "Draft",
                                     skiprows = [16,32], usecols = [0,1,2,3],
                                     header = 0)
        deck_sheet = pd.read_excel(file_name, sheet_name = "Play").dropna()

        #write player pick order- TODO: remove nested for and change to mapping
        for index, row in rank_sheet.iterrows():
            draft["players"].append({"name": row["Ranking"],
                                     "rank": index + 1})         
        for p in draft["players"]:
            p["seat"] = seat_to_player[p["name"]]
            for series_name, series in player_sheet.items():
                if series_name == p["name"]:
                    p["pick_order"] = series.to_list()
            for series_name, series in deck_sheet.items():
                if series_name == p["name"]:
                    p["decklist"] = series.to_list()
            
        draft_records.append(draft)
    f = open(f"{os.getcwd()}/output/raw.json", "w")
    f.write(json.dumps(draft_records, indent=4, default=str))
    f.close()

if __name__ == "__main__":
    generate_json()