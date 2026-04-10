import glob

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def verify_line_counts():
    print("=== SYNTHESIS INJECTION VERIFICATION (Script 2: Line count & Raw Text) ===")
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        print(f"Total lines in seed_data.json: {total_lines}")
        
        target_phrase = "<rule>MATHEMATICAL ANCHORING MANDATE:"
        appearances = 0
        rule_lines = []
        
        for i, line in enumerate(lines):
            if target_phrase in line:
                appearances += 1
                rule_lines.append(i + 1)
                
        print(f"Target rule '{target_phrase}' found exactly {appearances} times.")
        print(f"Found on lines: {', '.join(map(str, rule_lines))}")
            
        if appearances == 3:
            print("\n[SUCCESS] Raw text validation PASSED. All 3 matrices are successfully loaded into the file.")
        else:
            print("\n[FAILED] Expected 3 instances in text, found something else.")
            
    except Exception as e:
        print(f"[ERROR] Failed to read {SEED_FILE}: {e}")

if __name__ == "__main__":
    verify_line_counts()
