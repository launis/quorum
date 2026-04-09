import json
import shutil
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_tinydb_records(table_data):
    # TinyDB stores records as dict values inside the table dict
    if not table_data:
        return []
    return list(table_data.values())

def main():
    root_dir = Path("c:/src/quorum")
    db_path = root_dir / "data" / "db_v2.json"
    seed_path = root_dir / "backend_v2" / "seed" / "seed_data.json"
    
    db_backup = db_path.with_name("db_v2.backup.json")
    seed_backup = seed_path.with_name("seed_data.backup.json")
    
    # --- 1. BACKUP ---
    logging.info(f"Creating backups...")
    shutil.copy2(db_path, db_backup)
    shutil.copy2(seed_path, seed_backup)
    logging.info(f"Backed up DB to {db_backup}")
    logging.info(f"Backed up SEED to {seed_backup}")
    
    # --- 2. LOAD FILES ---
    logging.info("Reading source files...")
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            live_db = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read {db_path}: {e}")
        sys.exit(1)
        
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read {seed_path}: {e}")
        sys.exit(1)
        
    # --- 3. SURGICAL EXTRACTION ---
    logging.info("Extracting `output_profiles` ONLY from live database...")
    live_profiles_data = live_db.get('output_profiles', {})
    live_profiles_list = get_tinydb_records(live_profiles_data)
    
    if not live_profiles_list:
        logging.warning("No output_profiles found in live DB! Aborting to prevent data loss.")
        sys.exit(1)
        
    logging.info(f"Found {len(live_profiles_list)} output profiles in live database.")
    
    # Check old profile count for reporting
    old_profiles_list = seed_data.get('output_profiles', [])
    logging.info(f"Current seed config has {len(old_profiles_list)} output profiles.")

    # --- 4. SYNERGY CORRECTION (3d_matrix) ---
    updated_layout_count = 0
    for profile in live_profiles_list:
        if 'layouts' in profile:
            for layout in profile['layouts']:
                if layout.get('preset_view') == '3d_complex':
                    layout['preset_view'] = '3d_matrix'
                    updated_layout_count += 1
                    
    logging.info(f"Synergy correction complete: Converted {updated_layout_count} instances of '3d_complex' to '3d_matrix'.")
    
    # Replace ONLY the output_profiles in the seed dictionary
    seed_data['output_profiles'] = live_profiles_list
    
    # --- 5. WRITE AND VALIDATE ---
    logging.info("Writing updated seed file...")
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    # Python Audit (Runtime): Read immediately to verify
    logging.info("Running Python Audit (Runtime)...")
    with open(seed_path, 'r', encoding='utf-8') as f:
        audit_data = json.load(f)
        
    audit_profiles = audit_data.get('output_profiles', [])
    if len(audit_profiles) != len(live_profiles_list):
        logging.error("FATAL AUDIT MISMATCH: Written profiles length does not match extracted length.")
        sys.exit(1)
        
    complex_count = 0
    matrix_count = 0
    for profile in audit_profiles:
        if 'layouts' in profile:
            for layout in profile['layouts']:
                pv = layout.get('preset_view')
                if pv == '3d_complex':
                    complex_count += 1
                elif pv == '3d_matrix':
                    matrix_count += 1
                    
    if complex_count > 0:
        logging.error(f"FATAL AUDIT FAILURE: Found {complex_count} instances of '3d_complex' after conversion!")
        sys.exit(1)
        
    logging.info(f"Python Audit PASS. Verified {matrix_count} '3d_matrix' layouts inside seed file.")
    print("SUCCESS_FLAG")

if __name__ == '__main__':
    main()
