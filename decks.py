import json
from pathlib import Path
import helper
import copy

raw_path = Path.cwd().joinpath("output", "raw.json")
card_list_path = Path.cwd().joinpath("output", "card_list.json")
deck_name_path = Path.cwd().joinpath("input", "json", "deck_names.json")


def deck_name(pips, splash):
    with deck_name_path.open("r", encoding="utf-8") as f:
        deck_name_data = json.load(f)
    color_string = ""
    has_splash = False
    sorted_pips = dict(sorted(pips.items(), key=lambda x: x[1], reverse=True))
    for key, value in sorted_pips.items():
       # print(f"key - {key}, value - {value}, splash[key] - {splash[key]}")
        if value < 1 or splash[key] < 1:
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
    return color_string

def update_raw_colors():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with card_list_path.open("r", encoding="utf-8") as f:
        card_list_data = json.load(f)
    raw_rewrite = copy.deepcopy(raw_data)
    with deck_name_path.open("r", encoding="utf-8") as f:
        deck_name_data = json.load(f)

    for draft_i, draft in enumerate(raw_data):
        for player_i, player in enumerate(draft["players"]):
            pips, splash = {}, {}
            for card in player["decklist"]:
                #alias = helper.card_alias(card)
                #card_name = alias if alias is not None else card
                if card not in card_list_data:
                    #print(card)
                    continue
                card_dict = card_list_data[card]

                for key, value in card_dict["mana"]["pips"].items():
                    pips[key] = pips.get(key, 0) + value
                for key, value in card_dict["mana"]["splash"].items():
                    splash[key] = splash.get(key, 0) + value
            current_deck = raw_rewrite[draft_i]["players"][player_i]
            current_deck["pips"] = pips
            current_deck["splash"] = splash
            current_deck["deck_name"] = deck_name(pips, splash)
    
    with raw_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(raw_rewrite, indent=4))

def test_name():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    output = {}
    for draft in raw_data:
        for player in draft["players"]:
            run_name = f"{draft["draft_number"]}-{player["name"][0].lower()}"
            output[run_name] = player["deck_name"]



    test_path = Path.cwd().joinpath("output", "test.json")
    output = dict(sorted(output.items()))
    with test_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(output, indent=4))


if __name__ == "__main__":
    test_name()