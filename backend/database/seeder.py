import json
import os
from typing import Optional
from tinydb import TinyDB, Query
# from backend.config import DB_PATH, SEED_DATA_PATH # Removed

def seed_database(target_db_path: Optional[str] = None):
    """
    Seeds the database with initial data from seed_data.json.
    Supports both TinyDB (local) and Firestore (cloud) based on settings.
    
    Args:
        target_db_path (Optional[str]): Path to the database file (TinyDB only).
    """
    from backend.settings import get_settings
    settings = get_settings()
    
    # 1. Load Seed Data
    print(f"[Seeder] Loading seed data from: {settings.seed_data_path}")
    if not os.path.exists(settings.seed_data_path):
        print(f"[Seeder] Error: Seed data file not found at {settings.seed_data_path}")
        return

    try:
        with open(settings.seed_data_path, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
    except Exception as e:
        print(f"[Seeder] Error loading seed data: {e}")
        return

    # 2. Inject Code-Conf (Matrices)
    try:
        from backend.config.matrices import MATRICES
        print(f"[Seeder] Injecting {len(MATRICES)} Python-defined matrices.")
        for mat_id, mat_config in MATRICES.items():
            mat_dict = mat_config.model_dump()
            # Ensure ID and Type are set for the Component Table
            component_entry = {
                "id": mat_id,
                "type": "evaluation_matrix",
                "name": mat_dict.get("name", mat_id),
                "description": mat_dict.get("description", ""),
                "content": mat_dict # Store the full config as content
            }
            
            # Remove existing if present (to enforce code-conf authority)
            seed_data['components'] = [c for c in seed_data.get('components', []) if c.get('id') != mat_id]
            seed_data['components'].append(component_entry)
            
    except ImportError:
        print("[Seeder] Warning: could not import backend.config.matrices")
    except Exception as e:
         print(f"[Seeder] Error injecting matrices: {e}")

    # 3. Determine Mode
    is_firestore = settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db

    if is_firestore:
        print("[Seeder] Target: FIRESTORE (Cloud)")
        _seed_firestore(seed_data)
    else:
        final_db_path = target_db_path or settings.start_db_path
        print(f"[Seeder] Target: TinyDB (Local) at {final_db_path}")
        _seed_tinydb(final_db_path, seed_data)

def _seed_tinydb(db_path: str, seed_data: dict):
    try:
        db = TinyDB(db_path, encoding='utf-8')
        db.drop_tables()
        print("[Seeder] Cleared existing TinyDB tables.")
    except Exception as e:
        print(f"[Seeder] Error initializing TinyDB: {e}")
        return

    # Seed Tables
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')
    banned_phrases_table = db.table('banned_phrases')
    system_config_table = db.table('system_config')
    kb_table = db.table('knowledge_base')

    # Seed Components
    Component = Query()
    components_count = 0
    for component in seed_data.get('components', []):
        try:
            comp_id = component.get('id') or component.get('name')
            if not comp_id: continue
            
            if 'id' in component:
                components_table.upsert(component, Component.id == comp_id)
            else:
                components_table.upsert(component, Component.name == comp_id)
            components_count += 1
        except Exception: pass
    print(f"[Seeder] Upserted {components_count} components.")

    # Seed Steps
    Step = Query()
    count = 0
    for step in seed_data.get('steps', []):
        try:
            steps_table.upsert(step, Step.id == step['id'])
            count += 1
        except Exception: pass
    print(f"[Seeder] Upserted {count} steps.")

    # Seed Workflows
    Workflow = Query()
    count = 0
    for wf in seed_data.get('workflows', []):
        try:
            workflows_table.upsert(wf, Workflow.id == wf['id'])
            count += 1
        except Exception: pass
    print(f"[Seeder] Upserted {count} workflows.")
    
    # Seed Banned Phrases
    if 'banned_phrases' in seed_data:
        Phrase = Query()
        count = 0
        for item in seed_data['banned_phrases']:
            try:
                banned_phrases_table.upsert(item, Phrase.phrase == item['phrase'])
                count += 1
            except Exception: pass
        print(f"[Seeder] Upserted {count} banned phrases.")

    # Seed System Config
    if 'system_config' in seed_data:
        Config = Query()
        count = 0
        for item in seed_data['system_config']:
            try:
                system_config_table.upsert(item, Config.type == item['type'])
                count += 1
            except Exception: pass
        print(f"[Seeder] Upserted {count} system_config items.")

    # Seed Knowledge Base
    if 'knowledge_base' in seed_data:
        KB = Query()
        count = 0
        for item in seed_data['knowledge_base']:
            try:
                if 'term' in item:
                    kb_table.upsert(item, KB.term == item['term'])
                else:
                    kb_table.insert(item)
                count += 1
            except Exception: pass
    # Seed Model Registry
    if 'model_registry' in seed_data:
        Model = Query()
        count = 0
        for item in seed_data['model_registry']:
            try:
                model_registry_table.upsert(item, Model.id == item['id'])
                count += 1
            except Exception: pass
        print(f"[Seeder] Upserted {count} model_registry items.")

    print(f"[Seeder] Upserted {count} knowledge_base items.")
        
    print("[Seeder] TinyDB seeding completed.")

def _seed_firestore(seed_data: dict):
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        print("[Seeder] Error: firebase-admin not installed. Cannot seed Firestore.")
        return

    # Initialize App (if not already)
    if not firebase_admin._apps:
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"[Seeder] Error initializing Firebase: {e}")
            print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set.")
            return

    db = firestore.client()
    
    # 0. Clear existing collections (like drop_tables)
    print("[Seeder] Clearing existing Firestore collections...")
    collections_to_clear = ['components', 'steps', 'workflows', 'system_config', 'banned_phrases', 'knowledge_base', 'model_registry']
    
    def delete_collection(coll_ref, batch_size=400):
        docs = list(coll_ref.limit(batch_size).stream())
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        
        if deleted >= batch_size:
            return delete_collection(coll_ref, batch_size)
    
    for col_name in collections_to_clear:
        print(f"[Seeder] ...clearing {col_name}")
        delete_collection(db.collection(col_name))

    batch = db.batch()
    
    # Note: Firestore Batch limit is 500. We flush periodically.
    op_count = 0

    def commit_batch_if_full():
        nonlocal op_count, batch
        if op_count >= 400:
            batch.commit()
            batch = db.batch()
            op_count = 0
            print("[Seeder] ...Committing intermediate batch...")

    # 1. Components
    for item in seed_data.get('components', []):
        doc_id = item.get('id') or item.get('name')
        if doc_id:
            ref = db.collection('components').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    # 2. Steps
    for item in seed_data.get('steps', []):
        doc_id = item.get('id')
        if doc_id:
            ref = db.collection('steps').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    # 3. Workflows
    for item in seed_data.get('workflows', []):
        doc_id = item.get('id')
        if doc_id:
            ref = db.collection('workflows').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    # 4. System Config
    for item in seed_data.get('system_config', []):
        doc_id = item.get('type')
        if doc_id:
            ref = db.collection('system_config').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    # 5. Banned Phrases
    # These often don't have unique IDs, but we can make one hash or use phrase
    for item in seed_data.get('banned_phrases', []):
        phrase = item.get('phrase')
        if phrase:
            # Sanitize for ID or just use hash
            import hashlib
            doc_id = hashlib.md5(phrase.encode()).hexdigest()
            ref = db.collection('banned_phrases').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    # 6. Knowledge Base
    for item in seed_data.get('knowledge_base', []):
        # Prefer term, then id, then hash
        doc_id = item.get('term') or item.get('id')
        if not doc_id:
             import json
             doc_id = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
        
        # Sanitize ID (slashes not allowed in IDs usually, but Firestore handles some path chars differently)
        # Safer to replace slashes if term contains them
        doc_id = str(doc_id).replace('/', '_')
        
        ref = db.collection('knowledge_base').document(doc_id)
        batch.set(ref, item, merge=True)
        op_count += 1
        commit_batch_if_full()

    # 7. Model Registry
    for item in seed_data.get('model_registry', []):
        doc_id = item.get('id')
        if doc_id:
            ref = db.collection('model_registry').document(doc_id)
            batch.set(ref, item, merge=True)
            op_count += 1
            commit_batch_if_full()

    print("[Seeder] Firestore seeding completed successfully.")

if __name__ == "__main__":
    seed_database()

if __name__ == "__main__":
    seed_database()
