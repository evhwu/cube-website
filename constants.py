from typing import Final

COLOR_COMBOS : Final[dict[str,str]] = {
    "B": "Black",
    "G": "Green",
    "R": "Red",
    "U": "Blue",
    "W": "White",
    "BG": "Golgari",
    "BR": "Rakdos",
    "BU": "Dimir",
    "BW": "Orzhov",
    "GR": "Gruul",
    "GU": "Simic",
    "GW": "Selesnya",
    "RU": "Izzet",
    "RW": "Boros",
    "UW": "Azorius",
    "BGR": "Jund",
    "BGU": "Sultai",
    "BGW": "Abzan",
    "BRU": "Grixis",
    "BRW": "Mardu",
    "BUW": "Esper",
    "GRU": "Temur",
    "GRW": "Naya",
    "GUW": "Bant",
    "RUW": "Jeskai"
}
COLOR_HEX : Final[dict[str,str]] = {
    "Green": "ff78d05c",
    "Blue": "ff6FBBEA",
    "Red": "ffEA6F6F",
    "Purple":"ffAE6FEA"
}

SCRYFALL_SEARCH_RATE : Final[float] = 0.525
SCRYFALL_GENERAL_RATE : Final[float] = 0.125
USER_AGENT : Final[str] = "wucube/1.0"

SEAT_ORDER : Final[list] = ["Green", "Blue", "Red", "Purple"]

USERS_TO_NAMES : Final[dict[str, list]] = {
    "Alex" :    ["Alexotl"],
    "Bao" :     ["big big big big dumps"],
    "Evan" :    ["Nenni"],
    "Seymour" : ["shinydog"]
}
NAMES_TO_USERS : Final[dict[str, str]] = {
    "Alexotl" : "Alex",
    "big big big big dumps" : "Bao",
    "Nenni" : "Evan",
    "shinydog" : "Seymour"
}