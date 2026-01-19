
import json

path = r"c:\src\quorum\execution_dump.json"
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("results", {})
    score_cards = results.get("score_cards")
    
    print(f"Has score_cards: {score_cards is not None}")
    if score_cards is not None:
        print(f"Score Cards Count: {len(score_cards)}")
        print(json.dumps(score_cards, indent=2))
    else:
        print("Keys in results:", list(results.keys()))

except Exception as e:
    print(e)
