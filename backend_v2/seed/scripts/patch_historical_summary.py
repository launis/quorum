import json
from pathlib import Path

SEED_PATH = Path("backend_v2/seed/seed_data.json")


from typing import Any


def patch_synthesis(synthesis: dict[str, Any]) -> None:
    if "include_historical_summary" in synthesis:
        val = synthesis.pop("include_historical_summary")
        if val:
            synthesis["historical_context_mode"] = "SLIDING_WINDOW_3"
        else:
            synthesis["historical_context_mode"] = "DISABLED"


def main() -> None:
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Patch workflows
    for wf in data.get("workflows", []):
        for prf in wf.get("output_profiles", {}).values():
            if "synthesis" in prf:
                patch_synthesis(prf["synthesis"])
            for layout in prf.get("layouts", []):
                if "synthesis" in layout:
                    patch_synthesis(layout["synthesis"])

    # Patch output_profiles
    for prf in data.get("output_profiles", []):
        if "synthesis" in prf:
            patch_synthesis(prf["synthesis"])
        for layout in prf.get("layouts", []):
            if "synthesis" in layout:
                patch_synthesis(layout["synthesis"])

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
