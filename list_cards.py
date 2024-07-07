import json
import os

BASE_PATH = os.getcwd()

def generate_list():
    raw = open(os.path.join(BASE_PATH, 'raw.json'))
    data = json.load(raw)
    
    unique_cards = set()
    for d in data:
        for p in d["packs"]:
            for c in p["cards"]:
                unique_cards.add(c)

    raw.close()
    f = open(f"{BASE_PATH}/card_list.json", "w")
    f.write(json.dumps(sorted(unique_cards), indent=4))
    f.close()

generate_list()