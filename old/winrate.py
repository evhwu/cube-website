import json
import os

BASE_PATH = os.getcwd()

class WR_Player():
    def __init__(self, is_win, opponent):
        self.matchups = {}
        if is_win:
            self.matchups[opponent] = {"W" : 1, "L" : 0}
        else:
            self.matchups[opponent] = {"W" : 0, "L" : 1}
    def win(self, loser):
        if loser in self.matchups.keys():
            self.matchups[loser]["W"] = self.matchups[loser]["W"] + 1
        else:
            self.matchups[loser] = {"W" : 1, "L" : 0}
    def lose(self, winner):
        if winner in self.matchups.keys():
            self.matchups[winner]["L"] = self.matchups[winner]["L"] + 1
        else:
            self.matchups[winner] = {"W" : 0, "L" : 1}


def winrate():
    raw = open(os.path.join(BASE_PATH, 'raw.json'))
    data = json.load(raw)
    players = {}

    draft_limit = 120

    for draft in data:
        if int(draft["draft_number"]) > draft_limit:
            continue 
        for match in draft["matches"]:
            if match["winner"] in players.keys():
                players[match["winner"]].win(match["loser"])
            else:
                players[match["winner"]] = WR_Player(True, match["loser"])
            
            if match["loser"] in players.keys():
                players[match["loser"]].lose(match["winner"])
            else:
                players[match["loser"]] = WR_Player(False, match["winner"])
    raw.close()

if __name__ == "__main__":
    winrate()