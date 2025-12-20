import json

def find_step(step_id):
    with open('backend/database/seed_data.json', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if f'"{step_id}"' in line:
            print(f"Found {step_id} at line {i+1}")
            return

    print(f"{step_id} not found")

if __name__ == "__main__":
    find_step("step_falsifier")
