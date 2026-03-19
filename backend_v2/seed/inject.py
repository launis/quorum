import json
import os

SEED_FILE = 'c:/src/quorum/backend_v2/seed/seed_data.json'
DB_FILE = 'c:/src/quorum/data/db_v2.json'

def create_variants():
    return {
        '1d_metrics': {
            'version': '1.0',
            'components': [
                {'type': 'header', 'title': '1D Metrics Overview'},
                {'type': 'metadata_header'},
                {'type': '1d_gauge', 'title': 'Score 1', 'data_path': '$results.score1_normalized'},
                {'type': '1d_gauge', 'title': 'Score 2', 'data_path': '$results.score2_normalized'},
                {'type': 'bibliography_footer'}
            ]
        },
        '2d_compare': {
            'version': '1.0',
            'components': [
                {'type': 'header', 'title': '2D Matrix Comparison'},
                {'type': 'metadata_header'},
                {'type': '2d_matrix', 'x_data_path': '$results.x_score', 'y_data_path': '$results.y_score'},
                {'type': 'evaluation_notes_panel', 'data_paths': ['$results.notes']},
                {'type': 'bibliography_footer'}
            ]
        },
        '3d_complex': {
            'version': '1.0',
            'components': [
                {'type': 'header', 'title': '3D Analytical View'},
                {'type': 'metadata_header'},
                {'type': 'grid_row', 'columns': 2, 'children': [
                    {'type': '3d_scatter', 'x_data_path': '$results.x', 'y_data_path': '$results.y', 'z_data_path': '$results.z'},
                    {'type': 'evaluation_notes_panel', 'data_paths': ['$results.notes']}
                ]},
                {'type': 'bibliography_footer'}
            ]
        }
    }

def inject_blueprints(filepath, is_seed=False):
    if not os.path.exists(filepath):
        print(filepath, 'not found')
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    injected = False
    if is_seed:
        # Array of workflows
        for wf in data.get('workflows', []):
            if 'render_blueprints' not in wf: wf['render_blueprints'] = {}
            wf['render_blueprints'].update(create_variants())
            print('Injected seed variants into', wf.get('id'))
            injected = True
            break
    else:
        # Dict of dicts (TinyDB)
        workflows_table = data.get('workflows', {})
        for doc_id, wf in workflows_table.items():
            if 'render_blueprints' not in wf: wf['render_blueprints'] = {}
            wf['render_blueprints'].update(create_variants())
            print('Injected DB variants into', wf.get('id'))
            injected = True
            break
            
    if injected:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

try:
    inject_blueprints(SEED_FILE, True)
    inject_blueprints(DB_FILE, False)
except Exception as e:
    print('Error:', e)
