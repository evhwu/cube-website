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
        