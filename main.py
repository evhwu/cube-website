from card import generate_card
import json
import os

BASE_PATH = os.getcwd()
save_path = os.path.dirname(f"{BASE_PATH}/cards/")

def main():
    card_list = open(os.path.join(BASE_PATH, 'card_list.json'))
    data = json.load(card_list)
    
    for d in data:
        generate_card(d)
    
    card_list.close()
    
    
if __name__ == "__main__":
    main()