import json
from pathlib import Path

raw_path = Path.cwd().joinpath("output", "raw.json")


players = ["Nenni", "shinydog", "Alexotl", "big big big big dumps"]

def passing_wr():
    results = {}
    for player in players:
        results[player] = {"wins": 0, "losses" : 0}
        for p2 in players:
            if p2 != player:
                results[player][p2] = {"wins": 0, "losses" : 0}


    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    for draft in raw_data["draft_records"]:
        pass_order = []
        for p in draft["players"]:
            pass_order.append((p["name"], p["seat"]))
        pass_order = [x[0] for x in sorted(pass_order, key =lambda x: x[1])]

        for match in draft["matches"]:
            results[match["winner"]]["wins"] += 1
            results[match["loser"]]["losses"] += 1

            pass_to_winner = pass_order.index(match["winner"]) -1
            if pass_to_winner == -1:
                pass_to_winner = 3
            results[match["winner"]][pass_order[pass_to_winner]]["wins"] +=1

            pass_to_loser = pass_order.index(match["loser"]) -1
            if pass_to_loser == -1:
                pass_to_loser = 3
            results[match["loser"]][pass_order[pass_to_loser]]["losses"] +=1

    for key, val in results.items():
        wr = val["wins"] / (val["wins"] + val["losses"]) * 100
        #print(f"{key} has a WR of {wr:.4f}")
        for ikey, ival in val.items():
            try:
                if ikey == "wins" or ikey == "losses":
                    continue
                iwr = ival["wins"] / (ival["wins"] + ival["losses"]) *100
                print(f"When {ikey} passes to {key}, {key}'s WR changes from {wr:.2f} to {iwr:.2f} ({(iwr-wr):.2f})")
            except: 
                print("ZERO")
        print()




passing_wr()