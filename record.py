import openpyxl
import os

save_path = os.path.dirname(f"{os.getcwd()}/archive/")

with open(f"{save_path}/input/player_results.txt", 'r', encoding="utf-8") as result:
    player_file = result.read().split('\n')
with open(f"{save_path}/input/pack_results.txt", 'r', encoding="utf-8") as result:
    pack_file = result.read().split('\n')

