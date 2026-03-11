import json
from pathlib import Path


from typing import Any

def update_seed_data() -> None:
    seed_path = Path(__file__).parent.parent / "seed" / "seed_data.json"

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    # 1. Update workflows input_mappings
    print("Updating workflows...")
    target_workflows = ["workflow_courtroom_20_full_audit", "workflow_courtroom_30_fused_critics"]
    for wf in data.get("workflows", []):
        if wf.get("id") in target_workflows:
            for step in wf.get("steps", []):
                new_mappings = {}
                mappings = step.get("input_mappings", {})
                has_inputs = False
                for k, v in mappings.items():
                    if isinstance(v, str) and v.startswith("$inputs."):
                        has_inputs = True
                    elif isinstance(v, str) and v.startswith("$steps."):
                        new_mappings[k] = v
                    else:
                        new_mappings[k] = v
                if has_inputs:
                    new_mappings["inputs"] = "$inputs"
                step["input_mappings"] = new_mappings
                print(f"Updated {wf['id']} step {step.get('id')} -> {new_mappings}")

    # 2. Update prompt_blocks
    print("Updating prompt_blocks...")

    # A. Block texts
    block_texts = {
        "block_globalcontext": "Sääntö nykyhetkestä, {{INPUTS_JSON}}-injektion käsittelystä ja rooleista.",
        "block_headerinstructions": (
            '"Chain-of-Thought" sääntö reasoning_trace vaatimus, ja '
            '"Driver vs Passenger" vertailu erotettuna AI-datasta.'
        ),
        "block_oprule2": "Jos 80% tekoälyn, pelkkää automaatiota.",
        "block_oprule3": "Empiiriset teot vs. käyttäjän väitteet itsearvioinneissa.",
        "block_instructionnohallucination": "Pysyttävä datassa, ei keksittyjä esimerkkejä.",
        "block_instructionanon": "PII datan käsittely (\"Ei havaittu\").",
        "block_instructionnodataleak": (
            '"DATA_CHECKED_AND_SECURED" (Huge Data Protection). '
            'Estetään alkuperäisen massadatan litistäminen JSON schemaan.'
        ),
        "block_instructioncitationobligation": "Citation Snippet pakko (viitedata vaaditaan).",
        "block_taskguard": 'Input Hygiene Audit ja ohjeet risk_levelille ("KORKEA" riski lazy-prompteissa).',
        "block_taskanalyst": (
            "Truth protocol, Say-Do gap. Pydantic-valinnat "
            "(Verified/Violation/Hallucination), todisteet (rag_evidence)."
        ),
        "block_taskinteraction": "Driver Metrics. Riippuvuus, valintojen (Strategy/Archetype) täyttö.",
        "block_taskprofiler": 'Cognitive Bias Audit. "Illusion of Competence" Say-Do gap.',
        "block_tasklogician": (
            "Toulmin Audit. Syvä 6-osainen analysologia. Probative Value (KORKEA/KESKI/MATALA). "
            "*ÄLÄ LITISTÄ* sääntö."
        ),
        "block_taskfalsifier": (
            'Falsifiointi ja teroitettu iteraatiosilmukan arvio ("HEIKKO" fidelity auditissa). '
            "*ÄLÄ LITISTÄ* sääntö."
        ),
        "block_taskcausal": "Abduktiivinen ja vastafaktuaalinen päättely (Post Hoc testaus). *ÄLÄ LITISTÄ* sääntö.",
        "block_taskoverseer": "Hallucination Management, faktatarkistus. *ÄLÄ LITISTÄ* sääntö.",
        "block_taskarchivist": (
            'Best practices audit, compliance analyysi ("Critically Misaligned" vs "Strongly Aligned").'
        ),
        "block_taskjudge": "GRAND UNIFICATION. Kuljettaja vs Matkustaja. Hierarkinen pisteytys.",
        "block_taskcoach": "Kehityksen jalkauttaminen / Konstruktiivinen palaute.",
        "block_taskxai": "License Certification, moniagenttisen XAI-tuloksen lopputiivistys selkokielellä.",
        "block_taskpanel": (
            "Unified Critics tason kooste logiikasta, falsifioinnista, kausaalisuudesta, "
            "performatiivisuudesta ja hallusinaatioista (Rinnakkaisajojen yhteenveto)."
        )
    }

    # Helper for scale creation to ensure V2 No-String keys
    def make_scale(score: int, key: str) -> dict[str, Any]:
        return {
            "score": score,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": key, "en": key}
            },
            "claims": [
                {
                    "default_locale": "fi",
                    "translations": {"fi": key, "en": key}
                }
            ]
        }

    for block in data.get("prompt_blocks", []):
        block_id = block.get("id")

        if block_id in block_texts:
            if "description" not in block:
                block["description"] = {"default_locale": "fi", "translations": {}}
            block["description"]["translations"]["fi"] = block_texts[block_id]

        # B. Scales
        if block_id == "block_taskarchivist":
            block["type"] = "int"
            block["allow_decimals"] = False
            block["scales"] = [
                make_scale(1, "barsCompliance1"),
                make_scale(2, "barsCompliance2"),
                make_scale(3, "barsCompliance3"),
                make_scale(4, "barsCompliance4"),
                make_scale(5, "barsCompliance5"),
            ]
        elif block_id == "block_taskinteraction":
            block["type"] = "int"
            block["allow_decimals"] = False
            # Setting Arkkityyppi logic block array, wait.
            # The prompt_block can only have one scale array. Interaction has multiple scales
            # (Role Classification and Strategy). The plan notes:
            # *(Huom! Mikäli yhdessä blokissa on 2 numeroa... varmistamme toteutuksessa luodaanko oma blokki).*
            # To be safe and compliant, we'll keep the block as numeric and assign Role Classification to this block.
            block["scales"] = [
                make_scale(1, "barsRole1"),
                make_scale(2, "barsRole2"),
                make_scale(3, "barsRole3"),
                make_scale(4, "barsRole4"),
            ]
        elif block_id == "block_taskcausal":
            block["type"] = "int"
            block["allow_decimals"] = False
            block["scales"] = [
                make_scale(1, "barsSim1"),
                make_scale(2, "barsSim2"),
                make_scale(3, "barsSim3"),
            ]
        elif block_id == "block_taskxai":
            block["type"] = "int"
            block["allow_decimals"] = False
            block["scales"] = [
                make_scale(0, "barsConf0"),
                make_scale(25, "barsConf25"),
                make_scale(50, "barsConf50"),
                make_scale(75, "barsConf75"),
                make_scale(100, "barsConf100"),
            ]
        elif block_id == "block_taskguard":
            block["type"] = "int"
            block["allow_decimals"] = False
            block["scales"] = [
                make_scale(1, "barsRisk1"),
                make_scale(2, "barsRisk2"),
                make_scale(3, "barsRisk3"),
            ]

    print("Writing back to seed_data.json...")
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    update_seed_data()
