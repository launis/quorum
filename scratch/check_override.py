import json

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    allowed = []

    def extract_tdas(obj):
        if isinstance(obj, dict):
            if "tda_assertions" in obj and isinstance(obj["tda_assertions"], list):
                for tda in obj["tda_assertions"]:
                    desc = tda.get("ai_rule_description", "")
                    if tda.get("allow_contextual_override"):
                        allowed.append(tda.get("tda_id", "unknown") + ": " + desc[:100] + "...")
            for k, v in obj.items():
                extract_tdas(v)
        elif isinstance(obj, list):
            for item in obj:
                extract_tdas(item)

    extract_tdas(data)

    print("ALLOWED TDAS:")
    for a in allowed:
        print(a)

except Exception as e:
    print("Error:", e)
