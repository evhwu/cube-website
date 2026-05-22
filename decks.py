import json
from pathlib import Path

raw_path = Path.cwd().joinpath("output", "raw.json")
tag_path = Path.cwd().joinpath("input", "json", "tags.json")

def format_deck_sample():
    output = {"sample" : [],
              "testing" : []}
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f) 
    with tag_path.open("r", encoding="utf-8") as f:
        tag_data = json.load(f) 
    for draft in raw_data["draft_records"]:
        for player in draft["players"]:
            temp_name = f"{draft["draft_number"]}-{player["name"][0].lower()}"
            output["testing"].append({
                "name": temp_name,
                "decklist": player["decklist"]
            })
            if temp_name in tag_data and tag_data[temp_name]:
                output["sample"].append({
                    "name": temp_name,
                    "decklist": player["decklist"],
                    "tags": tag_data[temp_name]
                })
    sample_path = Path.cwd().joinpath("output", "sample.json")
    testing_path = Path.cwd().joinpath("output", "testing.json")
    with sample_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(output["sample"], indent=4))
    with testing_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(output["testing"], indent=4))

def test_name():
    with raw_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    output = {}
    pips_del = {}
    for draft in raw_data["draft_records"]:
        for player in draft["players"]:
            run_name = f"{draft["draft_number"]}-{player["name"][0].lower()}"
            output[run_name] = player["deck_name"]
            pips_del[run_name] = {"pips" : player["pips"],
                                  "splash" : player["splash"],
                                  "sources" : player["sources"]}

    test_path = Path.cwd().joinpath("output", "test.json")
    output = dict(sorted(output.items()))
    with test_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(output, indent=4))
    
    answer_path = Path.cwd().joinpath("input","json", "answer_sheet.json")
    with answer_path.open("r", encoding="utf-8") as f:
        answers = json.load(f)
    
    diff = {}
    for key, value in answers.items():
        if value != output[key]:
            temp_dict = pips_del[key]
            temp_dict["answer"] = value
            temp_dict["generated"] = output[key]
            diff[key] = temp_dict
    print("hehe")


if __name__ == "__main__":
    format_deck_sample()