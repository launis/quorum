
import json

path = r"c:\src\quorum\execution_dump.json"
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Top Level Keys:", list(data.keys()))
    
    if "score_cards" in data:
         print("Found score_cards at top level!")
    else:
         print("score_cards NOT found at top level.")

except Exception as e:
    print(e)
