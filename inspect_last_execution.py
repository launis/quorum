import json
from tinydb import TinyDB

db = TinyDB(r'c:\Users\risto\OneDrive\quorum\data\db.json')
executions = db.table('executions').all()

if not executions:
    print("No executions found.")
else:
    last_exec = executions[-1]
    print(f"Execution ID: {last_exec.doc_id}")
    print(f"Status: {last_exec.get('status')}")
    
    result = last_exec.get('result', {})
    if result:
        print(f"Result keys: {list(result.keys())}")
        if 'xai_report_content' in result:
            print("xai_report_content: FOUND")
            print(f"Length: {len(result['xai_report_content'])}")
            print("Preview: " + result['xai_report_content'][:100] + "...")
        else:
            print("xai_report_content: NOT FOUND")
    else:
        print("Result is empty.")
