import os
import json
import requests
import io
from PIL import Image, ImageFont, ImageDraw

from pathlib import Path
from helper import get_oracle_path

output_path = Path.cwd().joinpath("output", "images")
raw_path = Path.cwd().joinpath("output", "raw.json")
oracle_path = get_oracle_path()

def generate_deck_images():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with oracle_path.open("r", encoding="utf-8") as f:
        oracle_data = json.load(f)

    for draft in raw_data:
        for player in draft["players"]:
            cmc = 0
            curve = [[]]
            for card in player["decklist"]:
                card_dict =  [entry for entry in oracle_data if entry['name'] == card and
                               entry["object"] == "card" and entry["layout"] != "token"]
                for card_entry in card_dict:
                    if card_entry["name"] == card:
                        temp_cmc = card_entry['cmc']
                        try:
                            temp_image_url = card_entry['image_uris']['normal']
                        except:
                            temp_image_url = card_entry['card_faces'][0]['image_uris']['normal']
                        temp_image = Image.open(io.BytesIO(requests.get(temp_image_url).content))
                        if cmc != temp_cmc:
                            curve.append([])
                            cmc = temp_cmc
                        curve[-1].append(temp_image)
                        break

            max_x = len(curve) * 488 + 110
            max_y = len(max(curve, key=len)) * 100 + 780
            new_image = Image.new('RGB', (max_x, max_y))
            x = 0
            y = 100
            for mana_cost in curve:
                for card in mana_cost:
                    new_image.paste(card, (x, y))
                    y += 100
                x += 488
                y = 100
            
            myfont = ImageFont.truetype("arial.ttf", 72)
            draw = ImageDraw.Draw(new_image)
            x = (max_x - draw.textlength(player["deck_name"], font=myfont)) / 2
            draw.text((x, 0), player["deck_name"], font = myfont, fill="white")
            
            temp_path = output_path / f"{draft["draft_number"]}-{player["name"][0].lower()}.png"
            new_image.save(temp_path)
            print(temp_path)
            del new_image

if __name__ == "__main__":
    generate_deck_images()