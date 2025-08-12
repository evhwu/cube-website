import json
import os

base_path = os.path.dirname(f"{os.getcwd()}/output/")

def generate_list():
    raw = open(os.path.join(base_path, 'raw.json'))
    data = json.load(raw)
    
    unique_cards = set()
    for d in data:
        for p in d["packs"]:
            for c in p["cards"]:
                unique_cards.add(c)

    raw.close()
    f = open(f"{base_path}/card_list.json", "w")
    f.write(json.dumps(sorted(unique_cards), indent=4))
    f.close()

generate_list()