<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: MULTILINGUAL RULE-BASED STEMMING IN ANCHOR VALIDATION

## 1. Executive Summary & Objective

**Objective:** Implement a lightweight, pure-Python multilingual rule-based stemming layer in `AnchorValidationService` using `snowballstemmer` to eliminate False Negatives (Type II errors / Recall collapse) caused by grammatical inflections, case endings, and suffix variations (specifically Finnish 15 noun cases, Swedish articles/declensions, English conjugations, German endings, and Hungarian agglutinations), while preserving zero-hallucination precision and fail-fast guarantees.

**Primary Problem Solved:** As proven in forensic audit `feature_audit_low_score_root_cause.md`, execution scores collapsed to 4.7/100 partially because strict character-level string distance algorithms (RapidFuzz Levenshtein) reject valid citations where grammatical inflections alter surface characters (specifically and exhaustively: *"johtajuudessaan"* vs. *"johtajuus"*, *"tavoitteisiin"* vs. *"tavoitteet"*), causing the lexical verifier to misdiagnose valid linguistic variations as hallucinations.

### The 6 Quorum Core Invariants:
1. **100% Pydantic V2 DTO:** All match results and state transitions encapsulated exclusively in immutable Pydantic V2 models (`ConfigDict(strict=True, extra="forbid", frozen=True)`).
2. **Zero Naked Dictionaries (Zero Dict Mandate):** Absolute ban on `dict[str, Any]`, untyped dictionary accumulators, `.get()` lookups in state transit, and subscript assignments (`d[k] = v`).
3. **Deterministic Fail-Fast:** If a citation fails lexical and morphological verification, the system raises `SemanticEvidenceError` immediately without silent degradation or warning-only bypasses.
4. **Zero Permissive Fallbacks:** No fuzzy semantic guessing, no synonym dictionaries, and no heuristic fallback chains. Only exact mathematical stem identity across known content words is permitted. If an alien word is present, it fails deterministically.
5. **Single Source of Truth (SSOT):** Centralized locale threshold resolution via `get_lexical_fuzz_threshold(locale)` in `backend_v2/settings.py` and centralized ISO language mapping via `SUPPORTED_STEMMER_LANGUAGES`.
6. **100% Code Reuse (Single Pipeline Law):** Zero parallel pipelines or duplicate verification engines. Surgical insertion directly into `AnchorValidationService._is_lexically_valid()`, preserving public method `validate_evidence()` signature and contract.

---

## 2. Scope & Target Boundaries

### Target Files:
- `[MODIFY]` `@[pyproject.toml]`: Declare pure-Python dependency `snowballstemmer>=2.2.0`.
- `[NEW]` `@[backend_v2/utils/linguistics/stemmer.py]`: Implement `StemmerService`, `BaseStemmer` protocol, `SnowballLanguageStemmer`, `PassthroughStemmer`, and `StemmedMatchResultDTO`.
- `[MODIFY]` `@[backend_v2/services/orchestrator/anchor_validation_service.py#L124-L221]`: Integrate Stage 3 Morphological Stemmed Sequence Verification into `_is_lexically_valid`.
- `[MODIFY]` `@[backend_v2/services/orchestrator/anchor_validation_service.py#L357-L436]`: Refactor `process_atom_evaluation` to eradicate duplicated bifurcated `_is_match` helper and delegate directly to `_is_lexically_valid`.
- `[NEW]` `@[backend_v2/tests/unit/utils/linguistics/test_stemmer.py]`: Comprehensive ISTQB test suite for multilingual stemming, subsequence matching, content word coverage, and entropy gates.
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L216-L224]`: Modernize `test_anchor_validation_absolute_strictness` removing artificial `with patch(...)` mock in favor of native execution under strictness 100.
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L240-L247]`: Update `test_anchor_validation_strictness_multiplier` with inflection, alien-rejection, and strictness boundary assertions.
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L318-L338]`: Purge duplicate copy-paste tests of `process_atom_evaluation` and duplicate `_make_atom` fixture through line 436, and purge unused imports (`patch`, `AtomResultDTO`, `SourceDocumentContext`, `ExecutionStatus`) under Phase 1 cleanups.
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L7-L27]`: Modernize `_make_atom` fixture from raw model_validate dicts to typed constructor instantiation under QGR029.
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L30-L50]`: Verify `process_atom_evaluation` with inflected quotes matching source documents.

### Context Files (Read-Only):
- `@[backend_v2/settings.py#L957-L978]`: SSOT for locale-dependent lexical fuzz thresholds (`get_lexical_fuzz_threshold`).
- `@[backend_v2/models/enums.py#L567-L570]`: Authoritative system enums (`ValidationThresholdRatio`).
- `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L171-L190]`: 1-hop caller using `strict_match`.
- `@[backend_v2/hooks/integrity.py#L118-L138]`: 1-hop caller using `calculate_fuzzy_score`.
- `@[backend_v2/services/mcp/mcp_tool_loop.py#L134-L541]`: 1-hop caller using `normalize_text_with_mapping` and `strict_match`.
- `@[docs/tiede.md]`: Academic foundations and lexical verification principles.

---

## 3. Five-Axis System 2 Deconstruction

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[pyproject.toml]`** | Banned ad-hoc regex word trimming, custom suffix stripping dictionaries, or loose string heuristics. | Official pure-Python `snowballstemmer>=2.2.0` implementing Martin Porter algorithmic stemmers. | Pruned heavy NLP frameworks (zero spaCy, zero Voikko C-binaries, zero NLTK, zero neural embeddings). | `uv sync` lockfile resolution and clean import verification via `python -c "import snowballstemmer"`. |
| **[NEW] `@[backend_v2/utils/linguistics/stemmer.py]`** | Banned naked dictionaries (`dict[str, Any]` in `_stemmer_cache`), anonymous tuples, untyped string returns, and unconstrained monotonic matching without a window contiguity guard. | Immutable `StemmedMatchResultDTO(ConfigDict(strict=True, extra="forbid", frozen=True))`, `BaseStemmer` Protocol, strictly typed `_stemmer_cache: ClassVar[dict[str, BaseStemmer]] = {}`, Candidate Window Discovery, and Content Word Coverage (`matched_content / total_content >= min_coverage`). | Pruned speculative morphological parsers; strictly map ISO locales to established Snowball language names with window contiguity guard (`token_span <= len(quote_tokens) + 15`). 30% Deletion Test: Pruned speculative n-gram caching and multi-tier morphology daemons, saving 450+ lines of speculative bloat while preserving 100% stemming precision. | Unit tests in `test_stemmer.py` verifying Finnish, Swedish, English, German, Hungarian, CJK passthrough, window contiguity bounds, and zero-division protection. |
| **`@[backend_v2/services/orchestrator/anchor_validation_service.py#L124-L221]`** | Banned bypassing lexical validation, relaxing RapidFuzz globally without linguistic grounding, or permitting fuzzy matches under absolute strictness (`strictness_level >= 100`). | Stage 3 morphological verification activated strictly when `strictness_level < 100` and order-preserving content stem coverage is satisfied. When `strictness_level >= 100`, unconditionally enforce `tier_threshold = 100.0`. | Pruned secondary LLM arbitration calls; execution remains 100% deterministic pure compute in Python memory. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`. |
| **`@[backend_v2/services/orchestrator/anchor_validation_service.py#L357-L436]`** | Banned bifurcated pipelines and duplicated inline `_is_match` helper with divergent additive modifiers (`+15.0, +10.0, -5.0, -20.0, -35.0`). | Sovereign Single Pipeline Law: `process_atom_evaluation` delegates quote verification directly to `AnchorValidationService._is_lexically_valid`. | Pruned parallel heuristic matching logic; all quote evaluation routes through one unified validation engine. | Automated unit tests in `test_anchor_validation_atom_result.py` verifying inflected quote matching through `process_atom_evaluation`. |
| **[NEW] `@[backend_v2/tests/unit/utils/linguistics/test_stemmer.py]`** | Banned happy-path-only tests or tautological mocks of stemmer return values. | ISTQB 7-partition matrix: exact match, inflected match, alien words, short word entropy gate, CJK passthrough, scrambled monotonic order, and window contiguity overflow. | Pruned duplicate fixture factories; use parameterized pytest cases across target languages. | Direct assertions verifying both positive inflection matches and negative alien-word rejections with real compute. |
| **`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L216-L224]`** | Banned artificial monkeypatch mock (`with patch(..., return_value=100.0)`) masking real threshold behavior. | Native assertion verifying `strictness_level=100` unconditionally bypasses Stage 3 morphological verification and fails non-exact quotes fast. | Pruned theater mocks; assert real zero-trust strictness gate. | Clean execution via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py -k test_anchor_validation_absolute_strictness`. |
| **`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L240-L247]`** | Banned unverified assertions and skipping absolute strictness boundary tests. | Deterministic assertions verifying inflected Finnish citations succeed at strictness 50, alien citations fail fast, and inflected citations fail fast at strictness 100. | Pruned redundant mock wrappers and duplicate test definitions. | Automated execution via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`. |
| **`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L318-L338]`** | Banned duplicate copy-paste tests and fixtures across test files, and lingering unused imports (`patch`, `AtomResultDTO`, `SourceDocumentContext`, `ExecutionStatus`). | Purge duplicate `process_atom_evaluation` copy-paste tests and duplicate `_make_atom` fixture spanning lines 318 through 436, and purge unused imports. | Pruned redundant test duplication across test files. | Clean execution via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`. |
| **`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L7-L27]`** | Banned raw dictionary payloads in `_make_atom` fixtures (`model_validate({...})`) under QGR029. | Modernized typed `AtomResultDTO(...)` constructor instantiation with strict typing. | Pruned loose dictionary instantiation in test fixtures. | Automated verification via `uv run python scripts/audit_dict_eradication.py --strict`. |
| **`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L30-L50]`** | Banned unverified atom result quote validation. | Reconciled single-responsibility unit test verifying `process_atom_evaluation` with inflected and alien quotes. | Pruned redundant test variations. | Automated execution via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py`. |

---

## 4. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="DEPENDENCY_DECLARATION">
    <action>Declare `snowballstemmer>=2.2.0` in `@[pyproject.toml]` under dependencies.</action>
    <action>Run `uv sync` to update `uv.lock` with deterministic package pinning.</action>
    <constraint invariant="zero_c_binaries">Verify `snowballstemmer` is pure-Python with zero C-extensions or OS-specific wheels.</constraint>
    <constraint invariant="single_source_of_truth">All model unit dependencies strictly declared in `@[pyproject.toml]`.</constraint>
  </step>

  <step id="2" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>Inspect `@[backend_v2/services/orchestrator/anchor_validation_service.py#L357-L436]` to refactor `process_atom_evaluation`, eradicating duplicated bifurcated `_is_match` helper and replacing it with direct delegation to `AnchorValidationService._is_lexically_valid`.</action>
    <action>Purge duplicate test_process_atom_evaluation_* tests and duplicate _make_atom fixture starting at `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L318-L338]` through line 436, cleaning up unused imports (`patch`, `AtomResultDTO`, `SourceDocumentContext`, `ExecutionStatus`).</action>
    <action>Modernize `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L216-L224]` in test_anchor_validation_absolute_strictness to remove artificial `with patch(...)` mock in favor of native execution under strictness 100.</action>
    <action>Reconcile test fixtures in `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L7-L27]` modernizing _make_atom from raw model_validate({...}) dictionary payloads to typed AtomResultDTO(...) constructor instantiation under QGR029.</action>
    <action>Ensure directory `backend_v2/utils/linguistics/` exists and contains an empty `__init__.py`.</action>
    <constraint invariant="scoped_boy_scout">Confine all modifications strictly to touched target boundaries.</constraint>
    <constraint invariant="zero_naked_dicts">Assert that no dictionary state transit exists in touched scope.</constraint>
    <constraint invariant="single_pipeline_law">Eliminate bifurcated `_is_match` logic in favor of unified `_is_lexically_valid` pipeline.</constraint>
  </step>

  <step id="3" name="STEMMER_SERVICE_IMPLEMENTATION">
    <action>Create [NEW] `@[backend_v2/utils/linguistics/stemmer.py]` implementing:</action>
    <action>1. `StemmedMatchResultDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` containing fields: `is_match: bool`, `similarity_score: float`, `matched_content_stems: list[str]`, `total_content_stems: int`, `content_coverage_ratio: float`, and `matched_source_span: str | None = None`.</action>
    <action>2. `BaseStemmer` Protocol defining `stem_word(word: str) -> str` and `stem_tokens(tokens: list[str]) -> list[str]`.</action>
    <action>3. `SnowballLanguageStemmer` wrapping `snowballstemmer.stemmer(lang)` with an internal class-level `_stemmer_cache: ClassVar[dict[str, BaseStemmer]] = {}` and an Entropy Gate: words with length strictly under 4 characters remain unstemmed.</action>
    <action>4. `PassthroughStemmer` returning words unchanged for non-inflected or unsupported languages (specifically and exhaustively: `zh`, `ja`, `ko`, and unmapped locales).</action>
    <action>5. SSOT language registry mapping ISO 639-1 language codes (specifically and exhaustively: `fi` -> `finnish`, `sv` -> `swedish`, `en` -> `english`, `de` -> `german`, `hu` -> `hungarian`, `tr` -> `turkish`, `fr` -> `french`, `es` -> `spanish`, `it` -> `italian`, `nl` -> `dutch`, `da` -> `danish`, `no` -> `norwegian`, `ru` -> `russian`).</action>
    <action>6. `StemmerService` providing `tokenize_content_words()`, `stem_text()`, and `match_stemmed_subsequence(quote, source_text, locale, min_coverage=DEFAULT_MIN_COVERAGE)` bound to explicit named constants `DEFAULT_MIN_COVERAGE: float = 0.80`, `MAX_WINDOW_TOKEN_PADDING: int = 15`, and `MIN_STEMMABLE_WORD_LENGTH: int = 4`, implementing Candidate Window Discovery, Content Word Coverage (`matched_content / total_content >= min_coverage`), Window Contiguity Guard (`token_span <= len(quote_tokens) + MAX_WINDOW_TOKEN_PADDING`), Zero-Division Protection (`if total_content == 0: return fallback`), and `similarity_score = content_coverage_ratio * 100.0`.</action>
    <constraint invariant="entropy_gate_invariant">Words with character length strictly under `MIN_STEMMABLE_WORD_LENGTH = 4` characters must never be mutated by the stemmer.</constraint>
    <constraint invariant="window_contiguity_guard">Matched token span in source text must not exceed quote content tokens length plus `MAX_WINDOW_TOKEN_PADDING = 15` to prevent stitching distant paragraphs.</constraint>
    <constraint invariant="zero_division_guard">If all tokens are under 4 characters, fall back safely to total token evaluation without division by zero.</constraint>
    <constraint invariant="zero_naked_dicts">All match outcomes must be returned strictly via `StemmedMatchResultDTO`, and internal cache must use `dict[str, BaseStemmer]`.</constraint>
    <constraint invariant="fail_fast_validation">If quote or source_text is empty or whitespace, return is_match=False with zero coverage and zero stems without exception leakage.</constraint>
  </step>

  <step id="4" name="ANCHOR_VALIDATION_SERVICE_INTEGRATION">
    <action>Modify `@[backend_v2/services/orchestrator/anchor_validation_service.py#L124-L221]` in `_is_lexically_valid`:</action>
    <action>1. Maintain Stage 1: Exact substring fast-path (`norm_text.find(norm_quote)`).</action>
    <action>2. Maintain Stage 2: Length-weighted RapidFuzz check (`score >= tier_threshold`).</action>
    <action>3. Add Stage 3: Morphological Stemmed Sequence Verification (executed strictly when `strictness_level < 100` and Stage 2 failed):</action>
    <action>   - When `strictness_level >= 100`, unconditionally set `tier_threshold = 100.0`, triggering immediate exact-match fail-fast.</action>
    <action>   - When `strictness_level < 100`, invoke `StemmerService.match_stemmed_subsequence(quote=quote, source_text=norm_text, locale=locale, min_coverage=min(0.80, tier_threshold / 100.0))`.</action>
    <action>   - If `stem_result.is_match`, accept citation and log structured RFC 7807 warning with telemetry tags (`rapidfuzz_score`, `stem_similarity_score`, `matched_content_stems`, `strictness_level`).</action>
    <action>4. Maintain Stage 4: `SequenceMatcher` coverage safety net (`coverage_pct >= safety_net`).</action>
    <action>5. If all stages fail: Return False immediately to trigger Fail-Fast `SemanticEvidenceError` in parent `validate_evidence`.</action>
    <action>Modify `@[backend_v2/services/orchestrator/anchor_validation_service.py#L357-L436]` in `process_atom_evaluation` to delegate quote validation directly to `AnchorValidationService._is_lexically_valid(quote=atom.source_quote, norm_quote=norm_quote, norm_text=norm_doc, strictness_level=strictness_level, locale=locale)`.</action>
    <constraint invariant="absolute_strictness_preservation">When `strictness_level >= 100` or `tier_threshold >= 100.0` (Absolute strictness mode), Stage 3 must be bypassed entirely to enforce 100% exact character match.</constraint>
    <constraint invariant="zero_permissive_fallbacks">Never accept a quote unless order-preserving stem coverage is mathematically proven.</constraint>
    <constraint invariant="code_reuse_sovereignty">Maintain existing `validate_evidence` public signature and reuse existing `normalize_text_with_mapping` pipeline.</constraint>
  </step>

  <step id="5" name="TEST_SUITE_IMPLEMENTATION">
    <action>Create [NEW] `@[backend_v2/tests/unit/utils/linguistics/test_stemmer.py]` asserting:</action>
    <action>1. Finnish stemming parity: *johtajuudessaan* and *johtajuus* resolve to identical stem *johtajuu*.</action>
    <action>2. Swedish stemming parity: *ledarskapet* and *ledarskap* resolve to identical stem *ledarskap*.</action>
    <action>3. English stemming parity: *leadership*, *leading*, and *leaders* resolve to valid stems.</action>
    <action>4. German and Hungarian stemming parity.</action>
    <action>5. CJK Passthrough invariance: Chinese and Japanese characters are unmutated.</action>
    <action>6. Entropy Gate test: short words (*"tie"*, *"on"*, *"ei"*) are unmutated.</action>
    <action>7. Subsequence matching: order-preserving match succeeds; inverted or alien words fail.</action>
    <action>8. Window Contiguity Guard test: tokens scattered across distant sentences exceed max token span and fail.</action>
    <action>Modify `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L216-L224]` to verify absolute strictness level 100 rejects non-exact inflected quotes without theater mocks.</action>
    <action>Modify `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L240-L247]` asserting:</action>
    <action>1. Finnish inflected quote (*"johtajuus ja selkeät tavoitteet"*) matches source text (*"Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."*) under strictness level 50.</action>
    <action>2. Negative test: completely different words (*"talousarvio ja budjetti"*) fail fail-fast with `SemanticEvidenceError`.</action>
    <action>3. Absolute strictness boundary test: under strictness level 100, inflected quote fails and requires 100% exact match.</action>
    <action>Modify `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L30-L50]` asserting that `process_atom_evaluation` successfully validates inflected quotes against source documents.</action>
    <constraint invariant="istqb_negative_partitions">Mandate a minimum of two negative test partitions asserting deterministic rejection of ungrounded text.</constraint>
    <constraint invariant="deceptive_mock_ban">Test with real compute and real string operations; zero mock return value assertions.</constraint>
  </step>

  <step id="6" name="QUALITY_GATE_VERIFICATION">
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/utils/linguistics/stemmer.py --test --ast-strict`.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.</action>
    <action>Execute full backend test suite to verify zero regressions across existing citation workflows.</action>
    <constraint invariant="zero_tolerance_audit_loop">All Ruff formatting, MyPy strict typing, and AST strict guardrails must pass with zero warnings.</constraint>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan

### Test Commands:
```powershell
# 1. Localized Unit Test Gates
uv run pytest backend_v2/tests/unit/utils/linguistics/test_stemmer.py -v
uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py -v
uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py -v

# 2. Strict AST & Quality Gate
uv run python scripts/backend_audit_loop.py backend_v2/utils/linguistics/stemmer.py --test --ast-strict
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict

# 3. Full Backend Audit Gate
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

### Red-Team Falsification Checklist:

1. **Anti-Happy-Path Mandate (ISTQB Boundary Coverage)**:
   - For every positive test partition (Finnish/Swedish/English inflections), there are at least two negative boundary partitions (ISTQB-P2 through ISTQB-P7).
   - Rejection is proven deterministic: alien words, scrambled order, and distant token spans must raise `SemanticEvidenceError` without permissive fallbacks.

2. **Entropy Gate Invariant (< 4 Characters)**:
   - Prevents catastrophic false-positive collisions on short acronyms, stop words, and prepositions (specifically: *"tie"*, *"on"*, *"ei"*, *"puu"*).
   - Words with length strictly under 4 characters must never be mutated by Snowball stemmers.

3. **Window Contiguity Guard (Anti-Chimera Paragraph Defense)**:
   - Unconstrained monotonic stem search could stitch together words from opposite ends of a 50-page document into a valid citation.
   - Enforce that the token distance between the first and last matched stem in the source text must not exceed `len(quote_content_tokens) + 15`. Any match spanning across paragraphs fails deterministically.

4. **Zero-Division & Empty Payload Boundary Defense**:
   - Quotes containing exclusively short words (specifically: *"on se ei"*) must fall back safely to total token evaluation without raising `ZeroDivisionError`.
   - Empty or whitespace quotes/documents return `is_match=False` with zero stems and 0.0 coverage immediately.

5. **Pure Python & Zero-C Extension Isolation**:
   - `snowballstemmer` is 100% pure Python with zero native C-binaries, preserving Windows 11 and cross-platform free-threading compatibility.
   - `_stemmer_cache: ClassVar[dict[str, BaseStemmer]] = {}` is strictly typed, eliminating naked dictionary leaks and cold-start latency.

6. **Cross-Surface & SDUI Parity**:
   - `AnchorValidationService` operates strictly in backend Phase 1/6 for quote verification.
   - Public signatures `validate_evidence() -> list[str] | None` and `process_atom_evaluation() -> AtomResultDTO` maintain 100% contract stability, ensuring zero breaking changes across Flutter, PDF, and SDUI surfaces.

### Anti-Happy-Path Test Scenarios & ISTQB 7-Partition Matrix:

| Partition ID | Partition Description | Input State | Expected Outcome | Proof Anchor |
| :--- | :--- | :--- | :--- | :--- |
| **ISTQB-P1** | Positive Inflection Equivalence | Finnish: *"sitoutui johtajuudessaan selkeisiin tavoitteisiin"* vs. quote *"johtajuus ja selkeät tavoitteet"*. | Stems match in monotonic order with coverage >= 80%. `is_match = True`, score >= tier_threshold. | `test_stemmer_finnish_inflections` |
| **ISTQB-P2** | Negative Alien Words Rejection | Source: *"organisaation kehitys ja strategiatyö"*; quote: *"taloudellinen tuottavuus ja kulusäästöt"*. | Stem overlap = 0%. `is_match = False`. Raises `SemanticEvidenceError`. | `test_stemmer_alien_words_rejected` |
| **ISTQB-P3** | Negative Scrambled Monotonic Order | Source: *"ensimmäinen toinen kolmas"*; quote: *"kolmas toinen ensimmäinen"*. | Order violation fails monotonic sequence alignment. `is_match = False`. | `test_stemmer_scrambled_order_rejected` |
| **ISTQB-P4** | Negative Window Contiguity Overflow | Source: *"johtajuus"* in paragraph 1 and *"tavoitteet"* in paragraph 10 (span > 50 tokens). | Exceeds `max_span = len(quote_tokens) + 15`. Anti-Chimera defense triggers. `is_match = False`. | `test_stemmer_window_contiguity_guard` |
| **ISTQB-P5** | Absolute Strictness Boundary | Strictness level 100 (`tier_threshold >= 100.0`). Source: *"sitoutui johtajuudessaan"*; quote: *"sitoutui johtajuuteen"*. | Stage 3 morphological verification bypassed. 100% exact match required. Fails with `SemanticEvidenceError`. | `test_anchor_validation_strictness_multiplier` |
| **ISTQB-P6** | Short Word Entropy Gate | Words strictly under 4 characters (specifically: *"tie"*, *"on"*, *"ei"*, *"puu"*). | Stemmer returns tokens 100% byte-identical without truncation or false collisions. | `test_stemmer_entropy_gate_short_words` |
| **ISTQB-P7** | CJK Passthrough Invariance | Chinese: *"组织领导与战略目标"*, Japanese: *"リーダーシップと戦略的目標"*. | `PassthroughStemmer` processes text without token modification or syntax errors. | `test_stemmer_cjk_passthrough` |

