
import json
from tinydb import TinyDB

def inspect_trace():
    db_path = 'c:\\Users\\risto\\OneDrive\\quorum\\data\\db.json'
    db = TinyDB(db_path)
    executions_table = db.table('executions')
    all_executions = executions_table.all()
    if not all_executions: return

    last_exec = all_executions[-1]
    trace = last_exec.get('trace', {})
    if not trace: return

    inputs = trace.get('inputs', {})
    h_len = len(inputs.get('history_text', ''))
    p_len = len(inputs.get('product_text', ''))
    
    profiler = trace.get('step_profiler', {}) or {}
    metrics = profiler.get('teksti_metriikka', {})
    
    print(f"INPUT_HISTORY_LEN: {h_len}")
    print(f"INPUT_PRODUCT_LEN: {p_len}")
    print(f"METRICS_WORD_COUNT: {metrics.get('word_count')}")
    print(f"METRICS_SENTENCE_COUNT: {metrics.get('sentence_count')}")
    
    print(f"ANALYSIS_START: {str(profiler.get('analyysi', ''))[:50]}")

if __name__ == "__main__":
    inspect_trace()
