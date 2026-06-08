import os
from pathlib import Path


def clean_duplicate_tests():
    """Identifies duplicate test files in the root of backend_v2/tests/unit/
    that have already been moved to subdirectories (e.g. services, hooks, models, utils).
    Deletes the legacy duplicate from the root directory to prevent pytest conflict.
    """
    unit_dir = Path(r"C:\src\quorum\backend_v2\tests\unit")

    if not unit_dir.exists():
        print(f"Directory not found: {unit_dir}")
        return

    # Find all test files in subdirectories
    subdirectory_tests = {}
    for root, dirs, files in os.walk(unit_dir):
        if root == str(unit_dir):
            continue # skip root

        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                subdirectory_tests[file] = os.path.join(root, file)

    # Find test files in root and compare
    root_tests = [f for f in os.listdir(unit_dir) if os.path.isfile(os.path.join(unit_dir, f)) and f.startswith("test_") and f.endswith(".py")]

    deleted_count = 0
    for root_file in root_tests:
        if root_file in subdirectory_tests:
            old_path = os.path.join(unit_dir, root_file)
            new_path = subdirectory_tests[root_file]
            print(f"Duplicate found: {root_file}")
            print(f"  Legacy (deleting): {old_path}")
            print(f"  Kept: {new_path}")

            os.remove(old_path)
            deleted_count += 1

    print(f"\nCleanup complete. Deleted {deleted_count} duplicate legacy test files from the root of unit/.")

if __name__ == "__main__":
    clean_duplicate_tests()
