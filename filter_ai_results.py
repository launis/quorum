import json

try:
    with open(r'C:\src\quorum\LATEST_EXECUTION_EXPORT.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    ai_only = {}
    results = data.get('results', {})
    
    for step_id, step_data in results.items():
        # Jätetään pois "inputs" (jossa on ne isot raakatekstit) ja "metrics" (token-laskurit ym.)
        if 'outputs' in step_data:
            ai_only[step_id] = step_data['outputs']
            
    with open(r'C:\src\quorum\AI_RESULTS_ONLY.json', 'w', encoding='utf-8') as out:
        json.dump(ai_only, out, indent=2, ensure_ascii=False)
        
    print("SUCCESS: Cleaned AI results dumped.")
except Exception as e:
    print(f"Error: {e}")
