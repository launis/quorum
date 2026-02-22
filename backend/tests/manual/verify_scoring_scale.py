import json
from pathlib import Path

from backend.services.matrix_formatter import format_matrix_component


def verify_scoring_scale():
    # 1. Load seed_data.json
    seed_path = Path("backend/seed/seed_data.json").resolve()
    print(f"Loading seed data from: {seed_path}")

    with open(seed_path, encoding="utf-8") as f:
        seed_data = json.load(f)

    components = seed_data.get("components", [])

    # 2. Extract Matrices
    matrices = {}
    for comp in components:
        if comp.get("type") == "evaluation_matrix":
            matrices[comp["id"]] = comp

    if not matrices:
        print("ERROR: No matrices found in seed_data.json!")
        return

    with open("verification_report.txt", "w", encoding="utf-8") as out:
        # 3. Test Each Matrix
        for m_id, m_comp in matrices.items():
            out.write(f"\n{'=' * 60}\n")
            out.write(f"TESTING MATRIX: {m_id}\n")
            out.write(f"{'=' * 60}\n")

            try:
                prompt = format_matrix_component(m_comp)

                # Check for Key Phrases (Finnish)
                checks = [
                    "LAADULLISINA KIINTOPISTEINÄ",
                    "Käytä KOKO ASTEIKKOA",
                    "Interpoloi vapaasti",  # Only for range > 1
                    f"Scale: {m_comp['content']['scale']['min']}-{m_comp['content']['scale']['max']}",
                ]

                all_passed = True
                for check in checks:
                    if check in prompt:
                        out.write(f"[PASS] Found: '{check}'\n")
                    else:
                        # Special Case: Interpolation logic
                        rng = m_comp["content"]["scale"]["max"] - m_comp["content"]["scale"]["min"]
                        if "Interpoloi vapaasti" in check and rng <= 1:
                            out.write(f"[SKIP] Interpolation check skipped for small range ({rng})\n")
                            continue

                        out.write(f"[FAIL] Missing: '{check}'\n")
                        all_passed = False

                if all_passed:
                    out.write("\n-> SUCCESS: Prompt generated correctly.\n")
                    out.write("-" * 20 + "\n")
                    # Print snippet
                    lines = prompt.split("\n")
                    # Find Scoring Instruction block
                    for i, line in enumerate(lines):
                        if "[PISTEYTYSOHJE]" in line:
                            out.write("\nGenerated Instruction Snippet:\n")
                            out.write("\n".join(lines[i : i + 6]) + "\n")
                            break
                else:
                    out.write("\n-> FAILED: Prompt missing required elements.\n")

            except Exception as e:
                out.write(f"ERROR processing {m_id}: {e}\n")


if __name__ == "__main__":
    verify_scoring_scale()
