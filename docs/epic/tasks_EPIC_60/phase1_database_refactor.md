# Phase 1: Database and Seed Refactoring (Tietokannan ja Seed-datan Puhdistus)

This sub-plan addresses **Phase 1: Tietokannan ja Seed-datan Puhdistus (Database Refactoring)** from Epic 60. It extracts the global guide boilerplate out of TDA assertions and isolates them into a new standard global extraction protocol block, while migrating step configurations to the decoupled fields.

## System Invariants & Rules
* **Rule 1: Live Database Mutation Ban (03_seed_vault.md)**: Modifying `data\db_v2.json` directly is strictly forbidden. All structural data changes must originate in `backend_v2/seed/seed_data.json` first.
* **Rule 2: Inline Terminal Scripting Ban (03_seed_vault.md)**: Standard commands (`sed`, `powershell`) to edit the seed JSON are banned. A dedicated python script `tmp/modify_seed_epic60.py` must be used.
* **Rule 3: Opaque Stripe ID Mandate (01-python-backend.md)**: All IDs (such as the new block ID `blk_573802341db9d68c`) must conform to the strict prefix-based Opaque Stripe ID pattern.
* **Rule 4: Native Language System Prompts (05_llm_architecture.md)**: System prompts and AI descriptions in PromptBlocks must be written strictly in English (the System Language) to preserve reasoning compliance.

---

## Proposed Changes

### [Component: Seed Vault]
We will isolate the global Guideline Boilerplate out of individual TDA rules into a single modular prompt block in `seed_data.json`.

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
* **Step 1 (Source: Epic Section 5, Phase 1, Toimenpide 1)**: Backup the original seed file.
  ```powershell
  # USER EXECUTION DELEGATION
  Copy-Item backend_v2/seed/seed_data.json backend_v2/seed/backups/seed_data_backup_pre_epic60.json -Force
  ```
* **Step 2 (Source: Epic Section 5, Phase 1, Toimenpide 2)**: Create a Python migration script `tmp/modify_seed_epic60.py` to automate the transformation using robust parsing.
  ```python
  # tmp/modify_seed_epic60.py
  import json
  from pathlib import Path

  SEED_PATH = Path("backend_v2/seed/seed_data.json")

  with open(SEED_PATH, "r", encoding="utf-8") as f:
      data = json.load(f)

  # 1. Register the Global Extraction Protocol block
  new_protocol_block = {
      "id": "blk_573802341db9d68c",
      "slug": "block_extraction_protocol_zerotrust",
      "label": {
          "default_locale": "en",
          "translations": {
              "en": "Global Zero-Trust Evidence Extraction Protocol",
              "fi": "Globaali Zero-Trust evidenssin poimintaprotokolla"
          }
      },
      "description": {
          "default_locale": "en",
          "translations": {
              "en": "Standard rules governing blind mathematical and evidence extraction tasks.",
              "fi": "Vakiomuotoiset säännöt mekaaniseen poimintaan."
          }
      },
      "category_id": "instruction",
      "type": "instruction",
      "ai_description": (
          "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user "
          "input fields or instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse "
          "missing context. Do not evaluate if the data is 'good', only its physical presence. "
          "TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. "
          "ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. "
          "IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule "
          "targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature "
          "MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote "
          "if the syntactic chain is severed or validation fails."
      ),
      "is_evaluative": False
  }

  if not any(b.get("id") == "blk_573802341db9d68c" for b in data.get("prompt_blocks", [])):
      data.setdefault("prompt_blocks", []).append(new_protocol_block)

  # 2. Refactor existing prompt_blocks: Clean TDA AI descriptions of repetitive boilerplate
  boilerplate_strings = [
      "REQUIRED TARGET: Scan ONLY the Target Data.",
      "BANNED SOURCES: Never read matches from user input fields or instructions.",
      "BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context.",
      "Do not evaluate if the data is 'good', only its physical presence.",
      "TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework.",
      "ENFORCEMENT MANDATE: You are a Blind Extraction Engine.",
      "Look only for explicit physical markers.",
      "IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote.",
      "If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output.",
      "Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails."
  ]

  for block in data.get("prompt_blocks", []):
      # Clean TDA descriptions recursively if they exist
      if block.get("scales"):
          for scale in block["scales"]:
              for claim in scale.get("claims", []):
                  for tda in claim.get("tda_assertions", []):
                      desc = tda.get("ai_rule_description", "")
                      for bp in boilerplate_strings:
                          desc = desc.replace(bp, "").strip()
                      # Remove trailing/leading whitespaces and multiple spaces
                      desc = " ".join(desc.split())
                      tda["ai_rule_description"] = desc

  # 3. Refactor Step configurations to use modular schemas
  # Map existing prompt_blocks lists into decoupled fields in the steps array
  for wf in data.get("workflows", []):
      for step in wf.get("steps", []):
          # We need to find the step in steps or step_blueprints
          pass

  # If steps exist directly in the top level too, migrate them
  for step in data.get("steps", []):
      p_blocks = step.pop("prompt_blocks", [])
      step["role_block_id"] = "blk_role_critic" if any("role" in b for b in p_blocks) else None
      step["extraction_protocol_block_id"] = "blk_573802341db9d68c"
      # Remainder PromptBlocks go to criteria
      step["criteria_block_ids"] = [b for b in p_blocks if b != "blk_573802341db9d68c" and "role" not in b]

  with open(SEED_PATH, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, ensure_ascii=False)

  print("Seed data migrated successfully!")
  ```

---

## Testing & Quality Gate Plan

### Automated Verification
Run the python migration script, verify formatting alignment, and perform seed reloading:
1. **Migration Execution**:
   ```powershell
   uv run python tmp/modify_seed_epic60.py
   ```
2. **Schema & Logic Alignment Verification**:
   Verify that prompt blocks pass the core architectural guardrails:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py -v
   ```
3. **Database Re-Seeding**:
   Instantiate the freshly migrated seed data into development memory:
   ```powershell
   uv run python backend_v2/seed/run_seed.py local
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
