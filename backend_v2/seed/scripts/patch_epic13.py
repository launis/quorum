import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SEED_FILE = Path("backend_v2/seed/seed_data.json")

def generate_new_profiles() -> list[dict]:
    # 5 standard profiles as specified
    return [
        {
            "id": "prf_executive123",
            "slug": "executive_summary",
            "workflow_id": "wf_9d68c573802341db",
            "name": {
                "default_locale": "fi",
                "translations": {"en": "Executive Summary", "fi": "C-Tason Tiivistelmä"}
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "High-level overview focused on strategic indicators.",
                    "fi": "Korkean tason strateginen katsaus ylimmälle johdolle."
                }
            },
            "display_scale": "original",
            "synthesis": {
                "length_constraint": 1000,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {"en": "Executive Summary", "fi": "Johdon Tiivistelmä"}
                },
                "include_historical_summary": True,
                "enable_pii_masking": False,
                "allowed_exports": ["pdf", "docx"],
                "omit_empty_sections": True
            },
            "layouts": [
                {
                    "preset_view": "3d_complex",
                    "show_text": False,
                    "target_blocks": ["*"],
                    "steps": []
                }
            ]
        },
        {
            "id": "prf_techdeepdive",
            "slug": "technical_deep_dive",
            "workflow_id": "wf_9d68c573802341db",
            "name": {
                "default_locale": "fi",
                "translations": {"en": "Technical Deep Dive", "fi": "Tekninen Syväluotaus"}
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "Detailed analysis for domain experts.",
                    "fi": "Yksityiskohtainen katsaus ja lähdekritiikki asiantuntijoille."
                }
            },
            "display_scale": "original",
            "synthesis": {
                "length_constraint": 3000,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {"en": "Technical Analysis", "fi": "Tekninen Analyysi"}
                },
                "include_historical_summary": False,
                "enable_pii_masking": False,
                "allowed_exports": ["pdf", "docx", "raw_json"],
                "omit_empty_sections": False
            },
            "layouts": [
                {
                    "preset_view": "2d_compare",
                    "show_text": True,
                    "target_blocks": ["*"],
                    "steps": []
                }
            ]
        },
        {
            "id": "prf_publicstake7",
            "slug": "public_stakeholder",
            "workflow_id": "wf_9d68c573802341db",
            "name": {
                "default_locale": "fi",
                "translations": {"en": "Public Stakeholder Report", "fi": "Julkinen Sidosryhmäraportti"}
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "Redacted, safe report for public distribution.",
                    "fi": "Turvallinen ja maskattu raportti julkiseen jakeluun."
                }
            },
            "display_scale": "original",
            "synthesis": {
                "length_constraint": 1500,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {"en": "Public Report", "fi": "Julkinen Raportti"}
                },
                "include_historical_summary": False,
                "enable_pii_masking": True,
                "allowed_exports": ["pdf"],
                "omit_empty_sections": True
            },
            "layouts": [
                {
                    "preset_view": "1d_metrics",
                    "show_text": True,
                    "target_blocks": ["*"],
                    "steps": []
                }
            ]
        },
        {
            "id": "prf_coaching5432",
            "slug": "actionable_coaching",
            "workflow_id": "wf_9d68c573802341db",
            "name": {
                "default_locale": "fi",
                "translations": {"en": "Actionable Coaching", "fi": "Valmennusraportti"}
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "Focuses on explicit remediations and coaching steps.",
                    "fi": "Keskittyy korjaaviin toimenpiteisiin ja oppimiseen."
                }
            },
            "display_scale": "original",
            "synthesis": {
                "length_constraint": 2000,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {"en": "Coaching Report", "fi": "Kehitysraportti"}
                },
                "include_historical_summary": True,
                "enable_pii_masking": False,
                "allowed_exports": ["pdf"],
                "omit_empty_sections": True
            },
            "layouts": [
                {
                    "preset_view": "text_only",
                    "show_text": True,
                    "target_blocks": ["*"],
                    "steps": []
                }
            ]
        },
        {
            "id": "prf_holisticaudi",
            "slug": "holistic_audit",
            "workflow_id": "wf_9d68c573802341db",
            "name": {
                "default_locale": "fi",
                "translations": {"en": "Holistic Audit", "fi": "Kokonaisvaltainen Auditointi"}
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "End-to-end transparent system evaluation.",
                    "fi": "Kaikki osa-alueet avaava täydellinen auditointiraportti."
                }
            },
            "display_scale": "original",
            "synthesis": {
                "length_constraint": 4000,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {"en": "Holistic Audit", "fi": "Kokonaisvaltainen Auditointi"}
                },
                "include_historical_summary": True,
                "enable_pii_masking": False,
                "allowed_exports": ["pdf", "docx"],
                "omit_empty_sections": False
            },
            "layouts": [
                {
                    "preset_view": "default",
                    "show_text": True,
                    "target_blocks": ["*"],
                    "steps": []
                }
            ]
        }
    ]

def patch_seed_file():
    """Patches the seed_data.json to include strict Output Profiles."""
    if not SEED_FILE.exists():
        print(f"Error: {SEED_FILE} not found!")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Completely replace legacy output profiles with the 5 new standard profiles
    data["output_profiles"] = generate_new_profiles()

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Successfully patched {SEED_FILE}")

def patch_tinydb():
    """Drops old profiles and inserts new ones into TinyDB (if applicable locally)."""
    db_file = Path("data/db_v2.json")
    if not db_file.exists():
        print("Notice: No local db_v2.json found, skipping TinyDB patch.")
        return
        
    try:
        from tinydb import TinyDB
        db = TinyDB(str(db_file), encoding='utf-8')
        table = db.table('output_profiles')
        table.truncate()
        table.insert_multiple(generate_new_profiles())
        print(f"✅ Successfully patched {db_file} (output_profiles table)")
    except Exception as e:
        print(f"Failed to patch TinyDB: {e}")

if __name__ == "__main__":
    patch_seed_file()
    patch_tinydb()
    print("DONE: Seed and TinyDB Output Profiles migrated to Epic 13 standard.")
