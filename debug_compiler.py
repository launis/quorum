import json
import traceback
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

db = json.load(open('c:/src/quorum/data/db_v2.json', encoding='utf-8'))
mat = next((m for m in db['matrices'].values() if m.get('id') == 'matrix_input_processing'), None)
pc = PromptCompiler()
try:
    schema = pc.build_dynamic_schema('Test', [mat])
    print("SUCCESS", schema)
except Exception as e:
    print('ACTUAL ERROR:')
    traceback.print_exc()
