import json
from pathlib import Path

import pandas as pd

raw_path = Path.cwd().joinpath("output", "raw.json")

# Helper Functions
def get_oracle_data(check_raw=False) -> dict | None:
    """ Returns path to current oracle-cards json from Scryfall.

    All reference to Oracle should use this function as the path is constantly changing.

    Args:
        check_raw: If true, return only cards that exist in raw's card_list.
    """
    if check_raw:
        with raw_path.open(encoding="utf-8") as f:
            raw_data = json.load(f)
    def find_oracle() -> Path | None:
        oracle_path = Path.cwd().joinpath("input", "json")
        for f in oracle_path.iterdir():
            if "oracle-cards" in f.name:
                return f
        raise FileNotFoundError(f"oracle-cards not found in {oracle_path}")
    oracle_raw = find_oracle().open(encoding="utf-8")
    data_list: list[dict] = []
    # Need this looped loads to convert jsonl to opening load
    for line in oracle_raw:
        card_line = json.loads(line)
        if card_line["layout"] != "token":
            data_list.append(card_line)
    # Creates a dictionary with the card_name as key
    data_dict = {d["name"]: d for d in data_list}
    if check_raw:
        return {k: v for k, v in data_dict.items() if k in raw_data["card_list"]}
    return data_dict

def get_card_alias(card_name, shorten=True) -> str | None:
    """ For a given card_name, its given alias.
    
    This can either be only the first half of its name for flip / split cards or
    a given alias to a card if its naming causes errors in file processing.
    """
    # TODO: could also rewrite so card_name accepts a list as well, to 
    # reduce the number of times raw.json is opened
    if shorten:
        if "//" in card_name:
            return card_name.split(" // ")[0]
        return None
    # TODO: Currently, every instance of get_card_alias uses shorten.
    # When this second case occurs, rewrite and create an alias.json 
    else:
        raw_path = Path.cwd().joinpath("output", "raw.json")
        with raw_path.open(encoding="utf-8") as f:
            card_list = json.load(f)["card_list"]
        if "alias" in card_list[card_name]:
            return card_list[card_name]["alias"]
        return None

# XLSX Testing Functions
xlsx_path = Path.cwd().joinpath("input", "xlsx")
def find_xlsx_card(card_name) -> None:
    """ Returns each time a card_name appears and if they were run in the xlsx files."""
    for f in xlsx_path.iterdir():
        if f.suffix != ".xlsx":
            continue
        draft_sheet = pd.read_excel(f, sheet_name="Draft",
                                    skiprows=[16,32], usecols=[0,1,2,3],
                                    header=0)
        deck_sheet = pd.read_excel(f, sheet_name="Play", header=0)
        for series_name, series in draft_sheet.items():
            if card_name in series.values:
                run = "Run" if deck_sheet.isin([card_name]).any().any() else "Not Run"
                print(f"{f} - {series_name} - {run}")

def draft_exception_check(arc=True, siz=True, deal=True) -> None:
    """ Checks each xlsx file for aberrations in draft."""
    def arcane_savant_check() -> None:
        print("ARCANE SAVANT")
        for f in xlsx_path.iterdir():
            if f.suffix != ".xlsx":
                continue
            file_num = f.stem
            deck_sheet = pd.read_excel(f, sheet_name = "Play", usecols=[0,1,2,3])
            for player, col in deck_sheet.items():
                if "Arcane Savant" in col.values:
                    print(f"{file_num} - {player} - {col.dropna().size}")
    def deck_size_check() -> None:
        print("DECK SIZE")
        for f in xlsx_path.iterdir():
            if f.suffix != ".xlsx":
                continue
            file_num = f.stem
            deck_sheet = pd.read_excel(f, sheet_name = "Play", usecols=[0,1,2,3])
            for player, col in deck_sheet.items(): 
                if col.dropna().size != 40:
                    print(f"{file_num} - {player} - {col.dropna().size}")
    def deal_broker_check() -> None:
        """ Checks for trades done in draft by Deal Broker.
       
        Done by going through each xlsx. If for any players' decklist
        has a card that wasn't in their draft order, record it.
        """
        print("DEAL BROKER")
        for f in xlsx_path.iterdir():
            if f.suffix != ".xlsx":
                continue
            file_num = f.stem
            player_sheet = pd.read_excel(f, sheet_name="Draft", skiprows=[16,32],
                                        usecols=[0,1,2,3], header = 0)
            deck_sheet = pd.read_excel(f, sheet_name = "Play", usecols=[0,1,2,3])

            for player, col in deck_sheet.items():
                filtered_col = col[~col.str.contains("Snow-Covered", na=False)].dropna()
                for card in filtered_col:
                    if card not in player_sheet[player].values:
                        print(f"{f.stem} - {player} - {card}")

    if arc: arcane_savant_check()
    if siz: deck_size_check()
    if deal: deal_broker_check()

def get_xlsx_dates() -> None:
    """ Prints the date of each xlsx draft."""
    for f in xlsx_path.iterdir():
        if f.suffix != ".xlsx":
            continue
        date_sheet = pd.read_excel(f, sheet_name="Meta",header = None)
        print(f"{f.stem} - {date_sheet.iloc[0,0]}")

        
if __name__ == "__main__":
    
    ora = get_oracle_data()
    norm = ora["Llanowar Elves"]
    adv = ora["Embereth Shieldbreaker // Battle Display"]
    flip = ora["Jace, Vryn's Prodigy // Jace, Telepath Unbound"]
    print()
    
    