import os
import json
import requests
import io
from time import sleep
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

base_path = os.path.dirname(f"{os.getcwd()}/output/")

def generate_deck_images():
    raw = open(os.path.join(base_path, 'raw.json'))
    data = json.load(raw)


    for draft in data:
        for player in draft["players"]:
            cmc = 0
            curve = [[]]
            for card in player["decklist"]:
                response = requests.get(f"https://api.scryfall.com/cards/search?q={card}")
                card_dict = response.json()['data']
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
                sleep(0.125)

            max_x = len(curve) * 488 + 110
            max_y = len(max(curve, key=len)) * 100 + 680
            new_image = Image.new('RGB', (max_x, max_y))
            x = y = 0
            for mana_cost in curve:
                for card in mana_cost:
                    new_image.paste(card, (x, y))
                    y += 100
                x += 488
                y = 0
            temp_path = f"{base_path}/images/{draft["draft_number"]}-{player["name"][0].lower()}.png"
            new_image.save(temp_path)
            print(temp_path)
            del new_image

generate_deck_images()