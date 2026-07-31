import json

db_path = r'c:\src\quorum\data\db_v2.json'
with open(db_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

if 'executions' in d:
    d['executions'].clear()
    
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)

print("Kanta tyhjennetty ajoista (zombie-ajot poistettu)!")
