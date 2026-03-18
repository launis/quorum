import json

def extract_long_strings(obj):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'content_base64': continue
            results.extend(extract_long_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_long_strings(item))
    elif isinstance(obj, str) and len(obj) > 200:
        if '**user**:' in obj.lower() or '**ai**:' in obj.lower():
            results.append(obj)
    return results

e = json.load(open(r'c:\src\quorum\dump.json', 'r', encoding='utf-8'))
chats = extract_long_strings(e)
if chats:
    c = chats[0]
    print(c[:1500] + '\n\n[...] JATKUU YLI ' + str(len(c)) + ' MERKKIÄ LISÄÄ\n\n' + c[-500:].strip())
else:
    print("NO STRINGS WITH ROLES FOUND")
