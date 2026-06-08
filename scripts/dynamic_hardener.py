import argparse
import json
import re
from pathlib import Path
from typing import Any


def harden_seed_data(report_path: str) -> None:
    seed_path = Path("backend_v2/seed/seed_data.json")
    if not seed_path.exists():
        print(f"Error: Could not find {seed_path}")
        return

    report_file = Path(report_path)
    if not report_file.exists():
        print(f"Error: Could not find report {report_path}")
        return

    # Extract unstable TDAs
    unstable_tdas = set()
    with open(report_file, encoding="utf-8") as f:
        content = f.read()
        # Look for Atom-ID: `tda_...` (Entropia: 1.000
        matches = re.findall(r"Atom-ID:\s*`?(tda_[a-f0-9]{32})`?\s*\(Entropia:\s*1\.000", content)
        for m in matches:
            unstable_tdas.add(m)

    if not unstable_tdas:
        print("No unstable TDAs (Entropia: 1.000) found in the report.")
        return

    print(f"Found {len(unstable_tdas)} highly unstable TDAs. Applying hardening...")

    # Load seed data
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    negative_boundary = (
        " NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical "
        "exaggeration rather than literal evidence, reject. Do not infer unstated conclusions."
    )

    updates_made = 0

    def process_obj(obj: Any) -> None:
        nonlocal updates_made
        if isinstance(obj, dict):
            if "tda_assertions" in obj and isinstance(obj["tda_assertions"], list):
                for tda in obj["tda_assertions"]:
                    if tda.get("tda_id") in unstable_tdas:
                        tda["high_entropy"] = True
                        desc = tda.get("ai_rule_description", "")
                        if "NEGATIVE BOUNDARY" not in desc:
                            tda["ai_rule_description"] = desc + negative_boundary
                        updates_made += 1
            for _k, v in obj.items():
                process_obj(v)
        elif isinstance(obj, list):
            for item in obj:
                process_obj(item)

    process_obj(data)

    if updates_made > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Success: Hardened {updates_made} TDAs in seed_data.json.")
    else:
        print("No updates were made. The TDAs might already be hardened or missing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamically harden unstable TDAs based on an evaluation report.")
    parser.add_argument("--report", required=True, help="Path to the mismatch traces report markdown file.")
    args = parser.parse_args()

    harden_seed_data(args.report)
