import os
import json
import pandas as pd

BASE_PATH = os.getcwd()
save_path = os.path.dirname(f"{BASE_PATH}/archive/")
                        
def xlsx_to_json():
    archive_files = os.listdir(save_path)
    draft_records = []
    
    for f in archive_files:
        draft = {}
        file_num, file_ext = os.path.splitext(f)
        file_name = os.path.join(save_path, f)
        
        date_sheet = pd.read_excel(file_name,sheet_name="Date", header=None)    
        draft["draft_number"] = file_num
        draft["date"] = date_sheet.iloc[0,0]
        draft["patch"] = date_sheet.iloc[1,0]
        
        matches = []     
        match_sheet = pd.read_excel(file_name,sheet_name="Results", usecols=[0,1,2])
        is_swap = False 
        lastrow = pd.Series()
        def write_row(row):
            loser = row["Player 1"] if row["Winner"] == row["Player 2"] else row["Player 2"]
            matches.append({"winner" : row["Winner"], "loser" : loser})
        for index, row in match_sheet.iterrows():
            if index == 2:
                if row["Player 1"] == lastrow["Winner"] or row["Player 2"] == lastrow["Winner"]:
                    is_swap = True
                else:
                    write_row(row)
            elif is_swap:
                write_row(row)
                write_row(lastrow)
                is_swap = False
            else:
                write_row(row)
            lastrow = row
        draft["matches"] = matches
        
        pack_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                          usecols=[5,6,7,8], header=0)
        draft["packs"] = []
        for series_name, series in pack_sheet.items():
            packs = series.to_list()
            for i in range(3):
                draft["packs"].append({"player" : series_name.removesuffix(".1"),
                                       "number" : i + 1,
                                       "cards" : packs[i*15:((i + 1) * 15)]})
        
        rank_sheet = pd.read_excel(file_name,sheet_name="Results", usecols=[4], skiprows=[5,6])
        pick_order_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                          usecols=[0,1,2,3], header=0)
        play_sheet = pd.read_excel(file_name,sheet_name="Play").dropna()
        draft["players"] = []
        for index, row in rank_sheet.iterrows():
            draft["players"].append({"name": row["Ranking"],
                                     "place": index + 1})
        for p in draft["players"]:
            for series_name, series in pick_order_sheet.items():
                if series_name == p["name"]:
                    p["pick_order"] = series.to_list()
            for series_name, series in play_sheet.items():
                if series_name == p["name"]:
                    p["decklist"] = series.to_list()
             
        draft_records.append(draft)
        
    f = open(f"{BASE_PATH}/raw.json", "w")
    f.write(json.dumps(draft_records, indent=4))
    f.close()
        
        