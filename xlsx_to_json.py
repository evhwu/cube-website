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
        
        draft["draft_number"] = file_num

        draft_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                    usecols=[0,1,2,3,5,6,7,8], header=0)
        
        play_sheet = pd.read_excel(file_name,sheet_name="Play")
        result_sheet = pd.read_excel(file_name,sheet_name="Results")
        
        print(draft_sheet)
        
        #print(draft_sheet.iloc[3,3])
        #print(json.dumps(draft))
        