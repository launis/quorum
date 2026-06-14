# Phase 1: Backend Pydantic Schema Update

**Source:** Epic Phase 1 (Pydantic Skeeman Päivitys)

## Objective
Split the unstructured `concept_description` in `TDAAssertion` into structured granular fields for Anchor Target, Bounding Box Scope, and Extraction Rule.

## Scope
- **TARGET (Modify):** 
  - `backend_v2/models/v2_core.py`
  - `backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py` (and other related unit tests using TDAAssertion)
  - `backend_v2/llm/mock_data.py` (Update mock fixtures)
- **CONTEXT (Read-Only):**
  - `backend_v2/models/dtos/lightweight_matrix.py`

## Architectural Mandates
- **<rule num="2" id="strict_pydantic_v2_rust">**: Enforce `.model_validate()`, NEVER use the legacy `parse_obj()`. All NEW classes (EXCEPT Database boundary models per Rule 10) MUST define `model_config = ConfigDict(strict=True, extra="forbid")`. EXCEPTION: For existing models, DO NOT add model_config if it doesn't already exist, to prevent conflicts with Rule 85.
- **<rule num="7" id="zero_defaults_mandate">**: DTO models MUST NOT use default values if the missing data is critical. Standard functions and methods are STRICTLY PROHIBITED from using mutable types (e.g., list, dict) as default arguments (B006). Always use `None` and initialize the mutable object inside the function block.
- **<rule num="11" id="pydantic_native_field_priority">**: Prefer native Pydantic `Field(ge=..., max_length=...)` for simple integer/string bounds over custom `@field_validator` logic unless it requires Vertex AI float exceptions (Rule 5).
- **<rule num="65" id="pep750_t_strings_only">**: Construct dynamic LLM prompts and SQL statements exclusively utilizing Python 3.14 t-strings (Template Strings - PEP 750). The use of standard f-strings within critical data ingestion pathways is categorically forbidden due to inherent injection vulnerability vectors. Standard f-strings remain permitted for internal logging (`logger.info(f"...")`), debug output, and non-injection-sensitive formatting.
- **<rule num="77" id="zero_field_renaming_mandate"> & <rule num="84" id="pydantic_schema_freeze_mandate">**: We are explicitly overriding the Schema Freeze and Zero Field Renaming mandates via this Epic roadmap requirement to split `concept_description`.

## Implementation Steps
1. Open `backend_v2/models/v2_core.py`.
2. Locate the `TDAAssertion` class.
3. Update `concept_description` to specify: `Field(description="Vain tiivis kuvaus itse konseptista, ei ajo-ohjeita")`.
4. Add `anchor_target: str | None = Field(default=None, description="Mitä ankkuria etsitään (ent. STEP 1)")`.
5. Add `bounding_box_scope: Literal["sentence", "paragraph", "document", "adjacent_paragraphs"] = Field(default="paragraph")`.
6. Add `extraction_rule: str | None = Field(default=None, description="Varsinainen sääntö, joka datan on täytettävä (ent. EXTRACTION CONDITION)")`.
7. Update `backend_v2/llm/mock_data.py` to include these new fields in all JSON fixtures that mock `TDAAssertion`.
8. Fix any failing type hints or tests in `backend_v2/tests/unit/` caused by the schema change.

## Testing & Quality Gate Plan
- **Unit Tests:** Run Pytest on Pydantic domain models to ensure new fields are validated properly.
- **Universal Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/models --test` to verify no strictness or linting regressions occur. Naked execution of pytest is forbidden.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_tda_granular_schema_refactor_tracker.md`
