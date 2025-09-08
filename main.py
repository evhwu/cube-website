from xlsx import generate_json
import cards
import decks

def main():
    generate_json.generate_json()
    cards.generate_list()
    decks.update_raw_colors()
    
    decks.test_name()
if __name__ == "__main__":
    main()