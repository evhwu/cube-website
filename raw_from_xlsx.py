import json
import pandas as pd
from pathlib import Path
import helper

save_path = Path.cwd().joinpath("input", "xlsx")
raw_path = Path.cwd().joinpath("output", "raw.json")
oracle_path = helper.get_oracle_path()
exception_path = Path.cwd().joinpath("input", "json", "mana_exceptions.json")
deck_name_path = Path.cwd().joinpath("input", "json", "deck_names.json")

def raw_from_xlsx():
    draft_records = []
    unique_cards = set() # for card list
    
    def read_xlsx(): # reads each xlsx file and puts in draft record as dict
        for f in save_path.iterdir():
            if f.suffix != ".xlsx":
                continue
            file_num = f.stem

            date_sheet = pd.read_excel(f, sheet_name = "Date", header = None)
            match_sheet = pd.read_excel(f, sheet_name = "Results",
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
            pack_sheet = pd.read_excel(f, sheet_name="Draft",
                                    skiprows=[16,32], usecols=[5,6,7,8],
                                    header=0)
            seat_counter = 1
            seat_to_player = {}
            for series_name, series in pack_sheet.items():
                packs = series.to_list()
                unique_cards.update(packs)
                for i in range(3):
                    draft["packs"].append({"player" : series_name.removesuffix(".1"),
                                        "seat" : seat_counter,
                                        "number" : i + 1,
                                        "cards" : packs[i*15:((i + 1) * 15)]})
                seat_to_player[series_name.removesuffix(".1")] = seat_counter
                seat_counter += 1
            
            rank_sheet = pd.read_excel(f, sheet_name = "Results",
                                    usecols = [4], skiprows = [5,6])
            player_sheet = pd.read_excel(f, sheet_name = "Draft",
                                        skiprows = [16,32], usecols = [0,1,2,3],
                                        header = 0)
            deck_sheet = pd.read_excel(f, sheet_name = "Play").dropna()

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
    read_xlsx()

    with exception_path.open("r", encoding="utf-8") as f:
        exception_data = json.load(f)
    with oracle_path.open("r", encoding="utf-8") as f:
        oracle_data = json.load(f)
    for basic in exception_data["basics"]:
        unique_cards.add(basic)
    card_list = {}
    
    def card_list_entry(card_name): # translate oracle card data to usable format
        card_entry = [entry for entry in oracle_data if entry['name'] == card_name and
                    entry["object"] == "card" and entry["layout"] != "token"]
        card_dict = {}
        # special cases (ex. Lingering Souls) are in input/json/mana_exceptions.json
        if card_name in exception_data["exceptions"]:
            card_dict["mana"] = exception_data["exceptions"][card_name]["mana"]
        else:
            half_mana_string = ""
            # for multiple entries in Scryfall data, fix / add to exceptions immediately
            if len(card_entry) != 1: 
                print(f"Multiple oracle entries for {card_name}")
                mana_string = None
            # handling for multiface cards
            elif "card_faces" in card_entry[0]:
                type_lines = [d["type_line"] for d in card_entry[0]["card_faces"]]
                # filters out all non-mana faces (uncastable flips, lands)
                mana_cost_faces = [face for face in card_entry[0]["card_faces"] if face["mana_cost"] != ""]
                # multiple faces, count as half pips per side
                if any("Land" in w for w in type_lines) or len(mana_cost_faces) > 1:
                    half_mana_string = "".join(m["mana_cost"] for m in mana_cost_faces).lower()
                
                if len(mana_cost_faces) >= 1:
                    mana_string = mana_cost_faces[0]["mana_cost"]
                else:
                    mana_string = ""
            # normal handling
            else:
                mana_string = card_entry[0]["mana_cost"]
            def translate_mana_cost(mana_string):
                # TODO: check for if card faces are lands or adventures
                pips, splash = {}, {}
                if not mana_string:
                    return splash, pips
                # update when more colorless pips are introduced
                colorless_symbols = {"C", "X", "S"}
                symbols = mana_string.replace("{", "").split("}")
                splash_value = 1
                for s in symbols:
                    # skip colorless pips
                    if(not s or s.isnumeric() or s.upper() in colorless_symbols):
                        continue
                    # process colorless as half pips, including phyrexian mana
                    if("/" in s):
                        splash_value = 0.5
                        split_hybrid = s.split("/")
                        if "P" in split_hybrid:
                            split_hybrid.remove("P")
                        for c in split_hybrid:
                            pips[c] = pips.get(c, 0) + 0.5
                    # lowercase is set in mana_string for double face mana costs
                    elif s.islower():
                        pips[s.upper()] = pips.get(s.upper(), 0) + 0.5
                    else:
                        pips[s] = pips.get(s, 0) + 1
                for p in pips:
                    splash[p] = splash.get(p, 0) + splash_value
                return splash, pips

            if half_mana_string:
                splash, pips = translate_mana_cost(half_mana_string)
            else:
                splash, pips = translate_mana_cost(mana_string)
            color_profile = {"mana_cost" : mana_string,
                            "splash" : splash,
                            "pips" : pips}
            if "produced_mana" in card_entry[0]:
                color_profile["produced_mana"] = card_entry[0]["produced_mana"]
            card_dict["mana"] = color_profile
        
        if "image_uris" in card_entry[0]:
            img_url = card_entry[0]["image_uris"]["png"]
        elif "card_faces" in card_entry[0]:
            img_url = card_entry[0]["card_faces"][0]["image_uris"]["png"]
    
        card_dict.update({"tags": [], "img_url" : img_url})
        alias = helper.card_alias(card)
        if alias:
            card_dict["alias"] = alias
        return card_dict

    for card in unique_cards:
        card_list[card] = card_list_entry(card)
    card_list = dict(sorted(card_list.items()))

    ###############################################

    def deck_name(pips, splash, sources):
        with deck_name_path.open("r", encoding="utf-8") as f:
            deck_name_data = json.load(f)
        color_string = ""
        has_splash = False
        sorted_pips = dict(sorted(pips.items(), key=lambda x: -x[1]))
        for key, value in sorted_pips.items():
            # print(f"key - {key}, value - {value}, splash[key] - {splash[key]}")
            if value < 1 or splash[key] < 1 or key not in sources or sources[key] < 2:
                continue
            elif splash[key] <= 4:
                color_string += key.lower()
                has_splash = True
            else:
                color_string += key
        if not has_splash:
            if len(color_string) == 1:
                color_string = f"Mono-{deck_name_data["colors"][color_string]}"
            elif "".join(sorted(color_string)) in deck_name_data["colors"]:
                color_string = deck_name_data["colors"]["".join(sorted(color_string))]
        else:
            color_string = "".join(sorted(color_string, key=lambda c: c.islower()))
        return color_string

    for draft_i, draft in enumerate(draft_records):
        for player_i, player in enumerate(draft["players"]):
            pips, splash, sources = {}, {}, {}
            for card in player["decklist"]:
                #alias = helper.card_alias(card)
                #card_name = alias if alias is not None else card
                if card not in card_list:
                    #print(card)
                    continue
                card_dict = card_list[card]
                for key, value in card_dict["mana"]["pips"].items():
                    pips[key] = pips.get(key, 0) + value
                for key, value in card_dict["mana"]["splash"].items():
                    splash[key] = splash.get(key, 0) + value
                if "produced_mana" in card_dict["mana"]:
                    print(f"{card} - {card_dict["mana"]["produced_mana"]}")
                    for color in card_dict["mana"]["produced_mana"]:
                        if color != "C":
                            sources[color] = sources.get(color, 0) + 1
            current_deck = draft_records[draft_i]["players"][player_i]
            current_deck.update({"pips" : pips, "splash" : splash, "sources" : sources,
                                "deck_name" : deck_name(pips, splash, sources)})
    
    ###############################################
    record = {"card_list": card_list,
              "draft_records": draft_records}
    with raw_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=4, default=str))

if __name__ == "__main__":
    generate_json()