import argparse
import json
import re
import sys
from pathlib import Path

def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def extract_rule_blocks(file_path: Path) -> list[str]:
    if not file_path.exists():
        print(f"Error: Rules file {file_path} not found.")
        sys.exit(1)
    content = file_path.read_text(encoding="utf-8")
    matches = re.findall(r'<rule_block\s+id=["\']([^"\']+)["\']>', content)
    return matches

def cmd_generate(args: argparse.Namespace) -> None:
    repo_root = get_repo_root()
    core_rules = repo_root / ".agents" / "rules" / "00-antigravity-core.md"
    
    if args.type == "backend":
        domain_rules = repo_root / ".agents" / "rules" / "01-python-backend.md"
    elif args.type == "frontend":
        domain_rules = repo_root / ".agents" / "rules" / "02_flutter_desktop.md"
    else:
        print("Invalid type. Must be 'backend' or 'frontend'.")
        sys.exit(1)
        
    all_rules = extract_rule_blocks(core_rules) + extract_rule_blocks(domain_rules)
    
    seen: set[str] = set()
    unique_rules = []
    for r in all_rules:
        if r not in seen:
            seen.add(r)
            unique_rules.append(r)
            
    matrix = {
        "target_file": "",
        "rules": []
    }
    
    for rule_id in unique_rules:
        matrix["rules"].append({
            "rule_id": rule_id,
            "status": "PENDING",
            "justification": ""
        })
        
    out_dir = repo_root / "tmp"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "audit_matrix.json"
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)
        
    print(f"[SUCCESS] Generated strict JSON audit matrix at {out_path} with {len(unique_rules)} rules.")
    print("AI MUST fill out this JSON explicitly. 'status' must be PASS, FAIL, or NA.")

def cmd_verify(args: argparse.Namespace) -> None:
    matrix_path = Path(args.file)
    if not matrix_path.exists():
        print(f"Error: Matrix file {matrix_path} not found.")
        sys.exit(1)
        
    try:
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
        
    if not matrix.get("target_file"):
        print("ERROR: Validation Failed: 'target_file' is empty.")
        sys.exit(1)
        
    rules = matrix.get("rules", [])
    if not rules:
        print("ERROR: Validation Failed: No rules found in matrix.")
        sys.exit(1)
        
    errors = []
    valid_statuses = {"PASS", "FAIL", "NA"}
    
    for idx, rule in enumerate(rules):
        rule_id = rule.get("rule_id", f"unknown_rule_{idx}")
        status = rule.get("status", "").upper()
        justification = rule.get("justification", "").strip()
        
        if status not in valid_statuses:
            errors.append(f"Rule '{rule_id}' has invalid status '{status}'. Must be one of: {valid_statuses}")
            
        if not justification:
            errors.append(f"Rule '{rule_id}' is missing a justification.")
            
    if errors:
        print(f"ERROR: Validation Failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        print("\nThe AI MUST correct the JSON file before proceeding to fixes.")
        sys.exit(1)
        
    print(f"[SUCCESS] All {len(rules)} rules have been strictly validated for {matrix['target_file']}.")
    sys.exit(0)

def main() -> None:
    parser = argparse.ArgumentParser(description="Neuro-Symbolic Audit Matrix Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    gen_parser = subparsers.add_parser("generate", help="Generate a blank JSON matrix")
    gen_parser.add_argument("--type", required=True, choices=["backend", "frontend"], help="Target domain rules")
    
    ver_parser = subparsers.add_parser("verify", help="Verify a filled JSON matrix")
    ver_parser.add_argument("--file", required=True, help="Path to the filled JSON matrix")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "verify":
        cmd_verify(args)

if __name__ == "__main__":
    main()
