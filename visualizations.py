import json
import io
import requests

from PIL import Image, ImageFont, ImageDraw
from pathlib import Path

import constants
import helper

raw_path = Path.cwd().joinpath("output", "raw.json")
ml_path = Path.cwd().joinpath("output", "ml_output.json")
image_path = Path.cwd().joinpath("output", "images")

def first_pick_run_rate() -> None:
    """ Loops through each draft player to determine how often each run p1p1."""
    with raw_path.open(encoding="utf-8") as f:
        raw_data = json.load(f)
    # Creates a dictionary of Name : [0,0] pairs for each user
    results : dict[str, list[int]] = {k: [0,0] for k in constants.USERS_TO_NAMES }
    for draft in raw_data["draft_records"]:
        for player in draft["players"]:
            fp = player["pick_order"][0]
            user = constants.NAMES_TO_USERS[player["name"]]
            if fp in player["decklist"]:
                results[user][0] += 1
            else:
                results[user][1] += 1

    for k,v in dict(sorted(results.items(), key=lambda x: x[1][0])).items():
        print(f"{k} has run their first pick {v[0]} out of {v[0]+v[1]} times.")

def passing_wr() -> None:
    """ Prints winrates for each player based on who passes to them in draft."""
    with raw_path.open(encoding="utf-8") as f:
        raw_data = json.load(f)
    players: list[str] = list(constants.NAMES_TO_USERS)
    results = {
        player: {"wins": 0, "losses": 0} |
            {p2: {"wins": 0, "losses": 0} for p2 in players if p2 != player}
        for player in players
    }
    for draft in raw_data["draft_records"]:
        pass_order = []
        for p in draft["players"]:
            pass_order.append((p["name"], p["seat"]))
        pass_order = [x[0] for x in sorted(pass_order, key =lambda x: x[1])]

        for match in draft["matches"]:
            results[match["winner"]]["wins"] += 1
            results[match["loser"]]["losses"] += 1

            pass_to_winner = (pass_order.index(match["winner"]) - 1) % len(pass_order)
            results[match["winner"]][pass_order[pass_to_winner]]["wins"] +=1

            pass_to_loser = (pass_order.index(match["loser"]) - 1) % len(pass_order)
            results[match["loser"]][pass_order[pass_to_loser]]["losses"] +=1
    for key, val in results.items():
        wr = val["wins"] / (val["wins"] + val["losses"]) * 100
        for ikey, ival in val.items():
            try:
                if ikey == "wins" or ikey == "losses":
                    continue
                iwr = ival["wins"] / (ival["wins"] + ival["losses"]) *100
                print(f"When {ikey} passes to {key}, {key}'s WR changes from {wr:.2f} to {iwr:.2f} ({(iwr-wr):.2f})")
            except: 
                print("ZERO")
        print()

def generate_deck_images(min_max=False, colors=True, archetypes=False) -> None:
    """"""
    with raw_path.open(encoding="utf-8") as f:
        raw_data = json.load(f)
    if archetypes:
        with ml_path.open(encoding="utf") as f:
            ml_data = json.load(f)
    oracle_data = helper.get_oracle_data()
    CARD_WIDTH = 488
    CARD_V_GAP = 100

    for draft in raw_data["draft_records"]:
        if min_max:
            if min_max[0] > int(draft["draft_number"]) or min_max[1] < int(draft["draft_number"]):
                continue
        for player in draft["players"]:
            # Creates curve, which is a dictionary of cmcs : list of Image objects
            # TODO: differentiate between 0 cmc, nonland or land
            curve: dict[float, list] = {}
            for card in player["decklist"]:
                oracle_card = oracle_data[card]
                if "image_uris" not in oracle_card:
                    temp_image_url = oracle_card['card_faces'][0]['image_uris']['normal']
                else:
                    temp_image_url = oracle_card['image_uris']['normal']
                
                card_image = Image.open(io.BytesIO(requests.get(temp_image_url, headers=
                                          {"User-Agent" : constants.USER_AGENT}).content))
                if oracle_card["cmc"] in curve:
                    curve[oracle_card["cmc"]].append(card_image)
                else:
                    curve[oracle_card["cmc"]] = [card_image]

            # Generates the image based on created curve
            canvas_width = len(curve) * CARD_WIDTH
            canvas_height = max(len(cmc) for cmc in curve.values()) * CARD_V_GAP + 780
            new_canvas = Image.new("RGB", (canvas_width, canvas_height))

            for col, mana_cost in enumerate(curve.values()):
                for row, card_image in enumerate(mana_cost):
                    x = col * CARD_WIDTH
                    y = (row + 1) * CARD_V_GAP
                    new_canvas.paste(card_image, (x, y))

            # TODO: update for color and archetypes when ml is progressed
            # if colors or archetypes:
            draw = ImageDraw.Draw(new_canvas)
            title_font = ImageFont.truetype("arial.ttf", 72)
            x = (canvas_width - draw.textlength(player["deck_name"],
                                                font=title_font)) /2
            draw.text((x, 0), player["deck_name"], font=title_font, fill="white")
            """
            if archetypes:
                for m in ml_data:
                    if m["name"] == deck_code:
                        x = max_x - 600
                        y = max_y*0.7
                        for tag in m["new_tags"][0]:
                            draw.text((x,y), tag, font= myfont, fill="white")
                            y += 100
            """
            deck_code = f"{draft["draft_number"]}-{player["name"][0].lower()}"
            deck_path = image_path / f"{deck_code}.png"
            new_canvas.save(deck_path)
            print(deck_path)
            del new_canvas

if __name__ == "__main__":
    generate_deck_images()