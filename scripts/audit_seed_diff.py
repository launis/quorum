import json
from pathlib import Path

def normalize_dict(d):
    """Recursively remove 'id' and 'slug' keys from dictionaries and their nested structures."""
    if isinstance(d, dict):
        normalized = {}
        for k, v in d.items():
            if k not in ('id', 'slug', 'uid'):
                normalized[k] = normalize_dict(v)
        return normalized
    elif isinstance(d, list):
        return [normalize_dict(item) for item in d]
    else:
        return d

def compare_json_files(file1_path, file2_path, out_file):
    with open(out_file, 'w', encoding='utf-8') as out:
        def log(msg):
            out.write(msg + '\n')
            
        log(f"Comparing {file1_path} to {file2_path} (ignoring id, uid, slug)...")
        
        try:
            with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
                data1 = json.load(f1)
                data2 = json.load(f2)
        except Exception as e:
            log(f"Error reading files: {e}")
            return

        # Normalize both datasets
        norm_data1 = normalize_dict(data1)
        norm_data2 = normalize_dict(data2)

        # Check root keys
        keys1 = set(norm_data1.keys())
        keys2 = set(norm_data2.keys())
        
        if keys1 != keys2:
            log(f"Root keys differ!\nFile 1 has: {keys1}\nFile 2 has: {keys2}")
            return

        mismatches_found = False
        
        for collection_name in keys1:
            list1 = norm_data1[collection_name]
            list2 = norm_data2[collection_name]
            
            # Determine if it's a list or a dict
            if isinstance(list1, list) and isinstance(list2, list):
                if len(list1) != len(list2):
                    log(f"[{collection_name}] Length mismatch: {len(list1)} vs {len(list2)}")
                    mismatches_found = True
                    continue
                    
                for i, (item1, item2) in enumerate(zip(list1, list2)):
                    if item1 != item2:
                        log(f"[{collection_name}] Item {i} mismatch.")
                        # Let's find exactly what differs
                        if isinstance(item1, dict) and isinstance(item2, dict):
                            for k in set(item1.keys()).union(set(item2.keys())):
                                val1 = item1.get(k)
                                val2 = item2.get(k)
                                if val1 != val2:
                                    log(f"  Field '{k}' differs: {val1} != {val2}")
                        mismatches_found = True
            elif isinstance(list1, dict) and isinstance(list2, dict):
                if list1 != list2:
                   log(f"[{collection_name}] Dictionary mismatch.")
                   for k in set(list1.keys()).union(set(list2.keys())):
                       val1 = list1.get(k)
                       val2 = list2.get(k)
                       if val1 != val2:
                           log(f"  Field '{k}' differs: {val1} != {val2}")
                   mismatches_found = True
            else:
                if list1 != list2:
                    log(f"[{collection_name}] Type mismatch or general mismatch.")
                    mismatches_found = True

        if not mismatches_found:
            log("✅ SUCCESS: Data contents match perfectly (ignoring IDs and slugs).")
        else:
            log("❌ FAILURE: Mismatches found.")

if __name__ == "__main__":
    base_dir = Path(r"c:\src\quorum\backend\seed")
    compare_json_files(base_dir / "seed_data.json", base_dir / "seed_data copy.json", "diff_output.txt")
