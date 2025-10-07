import raw_from_xlsx
import cards
import decks

def main():
    raw_from_xlsx.generate_json()

    decks.test_name()
if __name__ == "__main__":
    main()