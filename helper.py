import os
import pandas as pd

BASE_PATH = os.getcwd()
save_path = os.path.dirname(f"{BASE_PATH}/archive/")
                        

def validate_decklist():
    archive_files = os.listdir(save_path)
    
    for f in archive_files:
        file_name = os.path.join(save_path, f)
        draft_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                    usecols=[0,1,2,3])
        play_sheet = pd.read_excel(file_name, sheet_name="Play")
        
        drafted_cards = {}
        for d_series_name, d_series in draft_sheet.items():
            drafted_cards[d_series_name] = []
            for card in d_series:
                drafted_cards.get(d_series_name).append(card)
        
        for p_series_name, p_series in play_sheet.items():
            for card in p_series:
                if not isinstance(card, str):
                    continue
                if "Snow-Covered" in card:
                    continue
                if card not in drafted_cards.get(p_series_name):
                    print(f"{f} - {p_series_name} - {card}")

def find_card(card_name, technical=False):
    print(card_name)
    
    archive_files = os.listdir(save_path)
    for f in archive_files:
        file_name = os.path.join(save_path, f)
        draft_sheet = pd.read_excel(file_name,sheet_name="Draft", skiprows=[16,32],
                                    usecols=[0,1,2,3], header=0)
        for series_name, series in draft_sheet.items():
            for card in series:
                if card == card_name:
                    print(f"{f} - {series_name}")
 
validate_decklist()