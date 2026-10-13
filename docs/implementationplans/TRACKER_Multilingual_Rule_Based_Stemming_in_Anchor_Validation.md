# Tracker: Multilingual Rule-Based Stemming in Anchor Validation
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]`
  - [ ] Step 1: DEPENDENCY_DECLARATION
  - [ ] Step 2: PRE_IMPLEMENTATION_CLEANUPS
  - [ ] Step 3: STEMMER_SERVICE_IMPLEMENTATION
  - [ ] Step 4: ANCHOR_VALIDATION_SERVICE_INTEGRATION
  - [ ] Step 5: TEST_SUITE_IMPLEMENTATION
  - [ ] Step 6: QUALITY_GATE_VERIFICATION
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/services/orchestrator/anchor_validation_service.py]
  - [ ] @[backend_v2/utils/linguistics/stemmer.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_topological_engine.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document eradication of bifurcated inline `_is_match` logic in `AnchorValidationService.process_atom_evaluation` and sovereign unification into `_is_lexically_valid`.
     - `@[ki_zero_permissive_typing.md]`: Document pure Pydantic V2 `StemmedMatchResultDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`, strictly typed stemmer cache `dict[str, BaseStemmer]`, and elimination of raw dictionary fixtures under QGR029.
     - `@[ki_topological_engine.md]`: Document Stage 3 Morphological Stemmed Sequence Verification within Phase 1 TDA atom anchoring and candidate window contiguity constraints.
  2. **Directory Reference Sync:**
     - Register `backend_v2/utils/linguistics/stemmer.py` under Pillar 1 (Mathematical Engines & System Invariants / Linguistic Utilities) in `@[.agents/rules/04_directory_reference.md]`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/01_system_context_and_invariants.md` describing the multi-stage lexical validation pipeline (Exact Match -> RapidFuzz -> Morphological Stemming Sequence -> Coverage Safety Net), Candidate Window Discovery, Window Contiguity Guard, and Entropy Gate in present tense.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After completing each cohesive step and running quality gates, instruct the user to execute an atomic `git commit` formatted according to Conventional Commits syntax (`<type>(<scope>): <summary>`). Explicitly list all staged files.
- **Single Pipeline Law**: All quote and anchor verification must flow through `AnchorValidationService._is_lexically_valid`. Bifurcated or parallel matching helpers in callers are strictly banned.
- **Zero Permissive Typing**: All match outcomes must be strictly returned via `StemmedMatchResultDTO`. No naked dictionaries, untyped tuples, or `.get()` fallbacks.
- **Absolute Strictness Invariant**: When `strictness_level >= 100` or `tier_threshold >= 100.0`, Stage 3 morphological verification must be bypassed unconditionally, requiring 100% exact character match.
- **Quality Gates**:
  - Python tests & static analysis: `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Structural markdown audit: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md`
- **Execution Mode**: Supports Continuous Full-Auto Mode via `/tier2-execute --full-auto`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Declare pure-Python `snowballstemmer>=2.2.0` in `pyproject.toml` and synchronize via `uv sync` | Step 1 | [ ] Pending |
| REQ-002 | Refactor `AnchorValidationService.process_atom_evaluation` to eradicate duplicated bifurcated `_is_match` helper and delegate directly to `_is_lexically_valid` | Step 2 | [ ] Pending |
| REQ-003 | Purge duplicate copy-paste tests and fixtures in `test_anchor_validation_service.py#L318-L338` through line 436 and clean up unused imports | Step 2 | [ ] Pending |
| REQ-004 | Modernize `test_anchor_validation_absolute_strictness` in `test_anchor_validation_service.py` to remove artificial `with patch(...)` mock in favor of native execution under strictness 100 | Step 2 | [ ] Pending |
| REQ-005 | Modernize `_make_atom` fixture in `test_anchor_validation_atom_result.py` from raw `model_validate({...})` dictionary payloads to typed `AtomResultDTO(...)` constructor instantiation under QGR029 | Step 2 | [ ] Pending |
| REQ-006 | Implement `StemmedMatchResultDTO` with strict frozen Pydantic V2 config and `BaseStemmer` Protocol in `backend_v2/utils/linguistics/stemmer.py` | Step 3 | [ ] Pending |
| REQ-007 | Implement `SnowballLanguageStemmer` with strictly typed `_stemmer_cache: ClassVar[dict[str, BaseStemmer]]` and Entropy Gate (< 4 characters) | Step 3 | [ ] Pending |
| REQ-008 | Implement `PassthroughStemmer` and SSOT language registry mapping ISO 639-1 language codes to Snowball algorithms (with CJK isolating passthrough) | Step 3 | [ ] Pending |
| REQ-009 | Implement `StemmerService` with Candidate Window Discovery, Content Word Coverage, Window Contiguity Guard, and Zero-Division Protection | Step 3 | [ ] Pending |
| REQ-010 | Integrate Stage 3 Morphological Stemmed Sequence Verification into `AnchorValidationService._is_lexically_valid` with absolute strictness bypass | Step 4 | [ ] Pending |
| REQ-011 | Implement comprehensive unit test suite in `backend_v2/tests/unit/utils/linguistics/test_stemmer.py` covering ISTQB 7-partition matrix | Step 5 | [ ] Pending |
| REQ-012 | Update unit tests in `test_anchor_validation_service.py` and `test_anchor_validation_atom_result.py` asserting inflection matching, alien word rejection, and strictness boundaries | Step 5 | [ ] Pending |
| REQ-013 | Execute localized audit loops and full backend quality gate ensuring zero warnings, zero AST violations, and 100% test pass | Step 6 | [ ] Pending |

# Session Handover Context

## Achieved
- Implementation Plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] successfully researched and red-team audited at Tier 0 with 100% boundary verification pass (`scripts/audit_markdown_boundaries.py` clean).
- Generated standalone plan execution tracker @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] establishing double-entry bookkeeping across 6 implementation steps, production hardening checklist, 13 traceability matrix requirements, and parameterized Tier 7 architectural sync directives.

## Learned
- **Pure-Python Free-Threading Compatibility**: `snowballstemmer` provides pure-Python Martin Porter algorithmic stemmers with zero C-extension overhead, 0ms cold-start penalty, and full Python 3.14 free-threading compatibility.
- **Single Pipeline Law Enforcement**: Eradicating inline `_is_match` in `process_atom_evaluation` eliminates divergent additive score modifiers (`+15.0, +10.0, -5.0, -20.0, -35.0`) in favor of centralized SSOT evaluation in `_is_lexically_valid`.
- **Anti-Chimera Paragraph Defense**: Unconstrained monotonic stem matching can stitch together disparate words from distant paragraphs; enforcing `token_span <= len(quote_tokens) + 15` mathematically protects citation integrity.
- **Entropy Gate (< 4 Characters)**: Words strictly under 4 characters must be protected from stemmer truncation to prevent false-positive collisions on short acronyms, stop words, and prepositions.

## Remaining
- Execute implementation via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]`.
- Execute post-implementation hardening and quality gates.
- Execute As-Built Architectural Sync via `/tier7-describe-architecture`.
- Execute Final Plan Audit via `/tier8-audit-plan`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md] @[docs/implementationplans/TRACKER_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]
```
