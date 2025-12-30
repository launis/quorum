import os
import shutil
import glob
import time

def clean_test_directories():
    # Find all directories starting with 'test_fusion_'
    pattern = "test_fusion_*"
    dirs = glob.glob(pattern)
    
    print(f"Found {len(dirs)} temporary test directories.")
    
    for d in dirs:
        if os.path.isdir(d):
            print(f"Removing {d}...")
            try:
                shutil.rmtree(d, ignore_errors=False)
            except OSError as e:
                print(f"  Error removing {d}: {e}")
                # Retry once after short sleep
                time.sleep(0.5)
                try:
                    shutil.rmtree(d, ignore_errors=True)
                    print(f"  Retry success for {d}")
                except Exception as e2:
                    print(f"  Retry failed for {d}: {e2}")

if __name__ == "__main__":
    clean_test_directories()
