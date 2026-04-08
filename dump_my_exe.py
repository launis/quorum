import json

execution_id_target = 'exe_ba2f098d475c4cfeb07ae9143ed673e0'

try:
    with open('c:\\src\\quorum\\data\\db_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    found_exe = None
    # Etsitään läpi kaikki TinyDB-taulut (esim. 'execution_records', 'executions', '_default' jne)
    for table_name, table_data in data.items():
        if isinstance(table_data, dict):
            for key, doc in table_data.items():
                if isinstance(doc, dict):
                    # TinyDB / backend_v2 asettaa dokumentille "id" kentän, tai "execution_id"
                    if doc.get('id') == execution_id_target or doc.get('execution_id') == execution_id_target:
                        found_exe = doc
                        break
        if found_exe:
            break

    if found_exe:
        with open('c:\\src\\quorum\\OMAT_AJOTIEDOT.json', 'w', encoding='utf-8') as out:
            json.dump(found_exe, out, indent=2, ensure_ascii=False)
        print("Löytyi! Tallennettiin tiedostoon: c:\\src\\quorum\\OMAT_AJOTIEDOT.json")
    else:
        print(f"Ajoa {execution_id_target} ei löytynyt mistään taulusta.")
        print("Tietokannasta löytyvät taulut ja niiden rivimäärät:")
        for t_name, t_data in dict(data).items():
            if isinstance(t_data, dict):
                print(f" - {t_name}: {len(t_data)} riviä")
                
except Exception as e:
    print(f"Virhe: {e}")
