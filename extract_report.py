import json
import os

try:
    with open('data/db_mock.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Find the latest execution
    latest_exec_id = max(db['executions'].keys(), key=int)
    result = db['executions'][latest_exec_id].get('result', {})
    
    report = result.get('xai_report_formatted')
    
    if report:
        with open('xai_raportti_talteen.md', 'w', encoding='utf-8') as f_out:
            f_out.write(report)
        print(f"Raportti tallennettu tiedostoon: xai_raportti_talteen.md (Execution ID: {latest_exec_id})")
    else:
        print("Raporttia ei l\u00f6ytynyt uusimmasta ajosta.")

except Exception as e:
    print(f"Virhe: {e}")
