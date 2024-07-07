import json
import os

BASE_PATH = os.getcwd()

def generate_card(card_name):
    raw = open(os.path.join(BASE_PATH, 'raw.json'))
    data = json.load(raw)
    
    output = {}
    
    def check_player(draft):
        seen = False 
        run = False 
        pick_number = 0
        active_player = ""
        for player in draft["players"]:
            if card_name in player["pick_order"]:
                active_player = player["name"]
                seen = True
                pick_number = ((player["pick_order"].index(card_name) ) % 15) +1
            if card_name in player["decklist"]:
                run = True
        return seen, run, pick_number, active_player
    
    output["name"] = card_name
    output["total"] = len(data)    
    output["seen"] = []
    output["run"] = []
    output["pick_number"] = 0
    output["wins"] = 0
    output["losses"] = 0 
    output["players"] = []
    
    for player in data[0]["players"]:
        output["players"].append({"name" : player["name"],
                                  "pick" : [],
                                  "run" : [],
                                  "pick_number" : 0,
                                  "wins" : 0,
                                  "losses" : 0})
    def calc_pick_number(p, s, np):
        return ((p * (s - 1)) + np) / s
    
    for draft in data:
        draft_no = draft["draft_number"]
        seen, run, pick_number, active_player = check_player(draft)
        if seen:
            output["seen"].append(draft_no)
            output["pick_number"] = calc_pick_number(output["pick_number"], len(output["seen"]), pick_number)
            for p in output["players"]:
                if active_player == p["name"]:
                    p["pick"].append(draft_no)

                    p["pick_number"] = calc_pick_number(p["pick_number"], len(p["pick"]), pick_number)
        if run:
            output["run"].append(draft_no)
            wins = 0
            losses = 0
            for m in draft["matches"]:
                if m["winner"] == active_player:
                    wins += 1
                if m["loser"] == active_player:
                    losses += 1
            output["wins"] += wins
            output["losses"] += losses
            
            for p in output["players"]:
                if active_player == p["name"]:            
                    p["run"].append(draft_no)
                    p["wins"] += wins
                    p["losses"] += losses
            
    raw.close()
    try:
        f = open(f"{BASE_PATH}/cards/{card_name}.json", "w")
        f.write(json.dumps(output, indent=4))
        f.close()
    except:
        print("skipped " + card_name)