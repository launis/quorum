import urllib.request, json
url = 'http://127.0.0.1:8000/v1/config/components'
req = urllib.request.urlopen(url)
data = json.loads(req.read())
item = next((i for i in data if i['id'] == 'ca9d9ae7-41ce-44d4-8a8f-efd2e0bd80a9'), None)
if item:
    with open('dump.json', 'w', encoding='utf-8') as f:
        json.dump(item, f, indent=2, ensure_ascii=False)
