# Phase 1: Foundation — New Directory Structure, Typed Protocol & AdapterContext DTO

**Overview:** Create the `backend_v2/services/sdui/adapters/` directory structure, define the frozen `AdapterContext` Pydantic DTO, define the `SduiAdapterProtocol`, and migrate the dispatch table and call site in `blueprint.py` from `Callable[..., list[AnySduiBlock]]` with kwargs scatter to `Callable[[AdapterContext], list[AnySduiBlock]]` with uniform single-DTO calling convention.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L86-L103] Phase 1

**Target Files:**
- @[c:\src\quorum\backend_v2\services\sdui\__init__.py] [NEW]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py] [NEW]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\__init__.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\__init__.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_base_adapter.py] [NEW]

**Context Files (READ-ONLY):**
- @[c:\src\quorum\backend_v2\models\enums.py#L117-L155] (VisualIntent, XaiExtensionType)
- @[c:\src\quorum\backend_v2\models\v2_core.py#L942] (MatrixScorecardRowDTO)
- @[c:\src\quorum\backend_v2\models\v2_core.py#L1493] (RenderedSynthesisCache)
- @[c:\src\quorum\backend_v2\models\v2_core.py#L1511] (ExecutionRecord)
- @[c:\src\quorum\backend_v2\models\view\sdui.py] (AnySduiBlock)
- KI: `sdui_adapter_decomposition` (specifically `ki_sdui_adapter_pattern.md`)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: This is the first phase. Verify the sdui/adapters/ directory does NOT already exist. Confirm by running list_dir on backend_v2/services/sdui/ and checking for a NotFound error or empty result.</action>
    <action>Look forward: Verify the dispatch table at @[c:\src\quorum\backend_v2\services\blueprint.py#L104-L111] still uses the untyped `Callable[..., list[AnySduiBlock]]` signature. If it has already been changed to `Callable[[AdapterContext], ...]`, STOP and request Course Correction.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md]) and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>AdapterContext uses model_config = ConfigDict(frozen=True, strict=True, extra="forbid")</item>
    <item>The dispatch table _target_block_hydrators uses dict[str, Callable[[AdapterContext], list[AnySduiBlock]]]</item>
    <item>The Callable import is at module level, NOT inside __init__</item>
    <item>Call site at blueprint.py dispatches via adapter_fn(context) with pre-constructed AdapterContext</item>
    <item>Zero .get() fallbacks in adapter code</item>
    <item>Zero bare except Exception: catch-alls</item>
    <item>Zero inline imports</item>
    <item>The word "Epic" does NOT appear in any added code</item>
  </dod_checklist>

  <anti_targets>
    <file>c:\src\quorum\backend_v2\models\view\sdui.py — Do NOT modify SDUI block models</file>
    <file>c:\src\quorum\backend_v2\models\v2_core.py — Do NOT modify existing DTOs</file>
    <file>c:\src\quorum\backend_v2\models\enums.py — Do NOT modify enums in this phase</file>
    <file>c:\src\quorum\backend_v2\services\execution.py — Do NOT touch external callers</file>
    <file>c:\src\quorum\backend_v2\worker.py — Do NOT touch the worker</file>
    <method>_extract_matrices_and_extensions — God Method is OUT OF SCOPE for Phase 1</method>
    <method>_hydrate_grouped_extensions_block — Adapter extraction is Phase 2</method>
    <method>_hydrate_penalties_block — Adapter extraction is Phase 3</method>
    <method>_hydrate_printable_sources_block — Adapter extraction is Phase 5</method>
    <method>Executive summary inline logic — Adapter extraction is Phase 4</method>
  </anti_targets>

  <step id="1" name="READ KNOWLEDGE ITEM">
    <action>Use view_file to read the canonical KI at C:\Users\risto\.gemini\antigravity-ide\knowledge\sdui_adapter_decomposition\artifacts\ki_sdui_adapter_pattern.md BEFORE writing any code.</action>
    <constraint invariant="knowledge_item_preflight">The executing agent MUST load the KI's canonical reference template, locked terminology, and AdapterContext schema into its context window before creating any files.</constraint>
  </step>

  <step id="2" name="CREATE DIRECTORY STRUCTURE">
    <action>Create the following empty files to establish the package hierarchy:
      1. @[c:\src\quorum\backend_v2\services\sdui\__init__.py] — Empty file
      2. @[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py] — Empty file
      3. @[c:\src\quorum\backend_v2\tests\unit\services\sdui\__init__.py] — Empty file
      4. @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\__init__.py] — Empty file
    </action>
  </step>

  <step id="3" name="CREATE base_adapter.py">
    <action>Create @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py] with the following exact contents:</action>
    <action>1. Module docstring: "Base adapter protocol and shared context DTO for SDUI presentation adapters."</action>
    <action>2. Top-level imports (ALL at module level, NO inline imports):
      - `from __future__ import annotations`
      - `from typing import Protocol`
      - `from pydantic import BaseModel, ConfigDict`
      - `from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, OutputProfile, RenderedSynthesisCache`
      - `from backend_v2.models.view.sdui import AnySduiBlock`
    </action>
    <action>3. Define AdapterContext class:
```python
class AdapterContext(BaseModel):
    """Immutable data envelope for all SDUI adapters.

    Constructed once by the BlueprintTransformer orchestrator before
    the dispatch loop. Passed identically to every adapter.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    execution: ExecutionRecord | None
    locale: str
    penalties_applied: list[str]
    mcp_audit_map: dict[str, MCPAuditTrace] | None
    global_score: float | None
    accumulated_extensions: dict[str, list[AnySduiBlock]]
    profile: OutputProfile
    profile_cache: RenderedSynthesisCache | None
```
    </action>
    <action>4. Define SduiAdapterProtocol class:
```python
class SduiAdapterProtocol(Protocol):
    """Protocol for all SDUI presentation adapters.

    Every concrete adapter MUST implement this interface with a single
    static build() method. The locked terminology (build, context,
    AdapterContext) is enforced by the KI sdui_adapter_decomposition.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context.

        Returns:
            Ordered list of polymorphic SDUI blocks.
        """
        ...
```
    </action>
    <constraint invariant="frozen_state_mutability">AdapterContext MUST use ConfigDict(frozen=True) to prevent downstream side effects.</constraint>
    <constraint invariant="strict_pydantic_v2_rust">AdapterContext MUST use ConfigDict(strict=True, extra="forbid") for Fail-Fast validation.</constraint>
    <contract_freeze>
      class AdapterContext(BaseModel): model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
      class SduiAdapterProtocol(Protocol): @staticmethod def build(context: AdapterContext) -> list[AnySduiBlock]
    </contract_freeze>
  </step>

  <step id="4" name="MODIFY blueprint.py — MOVE Callable IMPORT TO MODULE LEVEL">
    <action>In @[c:\src\quorum\backend_v2\services\blueprint.py], the `from collections.abc import Callable` inline import at line 103 (inside `__init__`) MUST be moved to the top-level imports section (after line 66).</action>
    <demolish>REMOVE: The inline `from collections.abc import Callable` at @[c:\src\quorum\backend_v2\services\blueprint.py#L103]. REPLACE WITH: Module-level import at the top of the file alongside other imports.</demolish>
    <constraint invariant="inline_imports_ban">All standard imports MUST be declared globally at the top of the file.</constraint>
  </step>

  <step id="5" name="MODIFY blueprint.py — IMPORT AdapterContext AND MIGRATE DISPATCH TABLE TYPE">
    <action>Add import for AdapterContext at the top of @[c:\src\quorum\backend_v2\services\blueprint.py]:
      `from backend_v2.services.sdui.adapters.base_adapter import AdapterContext`
    </action>
    <action>In `__init__`, change the dispatch table type annotation from:
      `self._target_block_hydrators: dict[str, Callable[..., list[AnySduiBlock]]]`
      to:
      `self._target_block_hydrators: dict[str, Callable[[AdapterContext], list[AnySduiBlock]]]`
    </action>
    <action>Wrap each existing hydrator method reference in a lambda that accepts AdapterContext but delegates to the old **kwargs method temporarily. This creates the bridge for incremental adapter extraction in subsequent phases:
```python
self._target_block_hydrators: dict[str, Callable[[AdapterContext], list[AnySduiBlock]]] = {
    TargetBlockType.PENALTIES_BLOCK: lambda ctx: self._hydrate_penalties_block(
        penalties_applied=ctx.penalties_applied,
    ),
    TargetBlockType.GLOBAL_SCORE_BLOCK: lambda ctx: [],
    TargetBlockType.AUDIT_TRAIL_BLOCK: lambda ctx: [],
    TargetBlockType.JARGON_RATIO_BLOCK: lambda ctx: self._hydrate_jargon_ratio_block(),
    TargetBlockType.PRINTABLE_SOURCES_BLOCK: lambda ctx: self._hydrate_printable_sources_block(
        profile_cache=ctx.profile_cache,
    ),
    TargetBlockType.GROUPED_EXTENSIONS_BLOCK: lambda ctx: self._hydrate_grouped_extensions_block(
        accumulated_extensions=ctx.accumulated_extensions,
    ),
}
```
    NOTE: The deferred placeholders (_hydrate_global_score_block, _hydrate_audit_trail_block) are replaced with inline `lambda ctx: []` since their methods already return `[]`. The _hydrate_jargon_ratio_block method returns a hardcoded ParagraphBlock — keep calling it via lambda until Phase 5a decisions.
    </action>
    <demolish>REMOVE: The old `Callable[..., list[AnySduiBlock]]` type annotation and the direct method references (self._hydrate_penalties_block, etc.). REPLACE WITH: Lambda-wrapped calls that accept AdapterContext and delegate to the existing methods with explicit keyword arguments.</demolish>
    <constraint invariant="adapter_context_immutability">The dispatch table MUST use Callable[[AdapterContext], list[AnySduiBlock]] — no **kwargs.</constraint>
  </step>

  <step id="6" name="MODIFY blueprint.py — MIGRATE DISPATCH CALL SITE">
    <action>At @[c:\src\quorum\backend_v2\services\blueprint.py#L1948-L1960], the dispatch call site currently passes 8 keyword arguments per call. Refactor to:
      1. BEFORE the dispatch loop (before line 1940), construct a single AdapterContext instance:
```python
adapter_context = AdapterContext(
    execution=execution,
    locale=locale,
    penalties_applied=penalties_applied,
    mcp_audit_map={t.id: t for t in mcp_audit_data} if mcp_audit_data else None,  # TYPE BRIDGE: convert list to dict
    global_score=global_score,
    accumulated_extensions=accumulated_extensions,
    profile=profile,
    profile_cache=profile_cache,
)
```
      2. Replace the kwargs scatter call at lines 1949-1958 with:
```python
hydrated_blocks = self._target_block_hydrators[str(target_k)](adapter_context)
```
    </action>
    <demolish>REMOVE: The 8-line kwargs scatter pattern at @[c:\src\quorum\backend_v2\services\blueprint.py#L1949-L1958]:
```python
hydrated_blocks = self._target_block_hydrators[str(target_k)](
    execution=execution,
    locale=locale,
    penalties_applied=penalties_applied,
    mcp_audit_data=mcp_audit_data,
    global_score=global_score,
    profile=profile,
    accumulated_extensions=accumulated_extensions,
    profile_cache=profile_cache,
)
```
REPLACE WITH: Single `adapter_context` pass.
    </demolish>
    <constraint>TYPE BRIDGE: The dispatch call site has `mcp_audit_data` (a list), but AdapterContext requires `mcp_audit_map` (a dict). The executing agent MUST convert it during construction: `mcp_audit_map={t.id: t for t in mcp_audit_data} if mcp_audit_data else None`.</constraint>
  </step>

  <step id="7" name="CREATE test_base_adapter.py">
    <action>Create @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_base_adapter.py] with the following tests:</action>
    <constraint invariant="anti_happy_path_mandate">For every positive test case, at least 2 negative tests are required.</constraint>
    <test_contracts>
      <test name="test_adapter_context_valid_construction" category="positive">
        <input>AdapterContext with all required fields set to valid values (execution=None, locale="fi", penalties_applied=[], mcp_audit_map=None, global_score=None, accumulated_extensions={}, profile=valid_output_profile_fixture, profile_cache=None)</input>
        <expected>Successfully creates a frozen AdapterContext instance</expected>
      </test>
      <test name="test_adapter_context_frozen_rejects_mutation" category="negative">
        <input>Attempt to set ctx.locale = "en" on a frozen AdapterContext instance</input>
        <expected>raises ValidationError (frozen model cannot be mutated)</expected>
      </test>
      <test name="test_adapter_context_forbids_extra_fields" category="negative">
        <input>AdapterContext(locale="fi", penalties_applied=[], ..., unknown_field="hax")</input>
        <expected>raises ValidationError (extra fields forbidden)</expected>
      </test>
      <test name="test_adapter_context_missing_required_field_raises" category="error_path">
        <input>AdapterContext(locale="fi") — missing penalties_applied, profile, accumulated_extensions, etc.</input>
        <expected>raises ValidationError (missing required fields)</expected>
      </test>
      <test name="test_adapter_context_strict_type_enforcement" category="boundary">
        <input>AdapterContext(locale=123, ...) — passing int instead of str for locale</input>
        <expected>raises ValidationError (strict=True enforces type)</expected>
      </test>
    </test_contracts>
  </step>

  <step id="8" name="RUN QUALITY GATE">
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/services/sdui --test</action>
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui --test</action>
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test</action>
    <action>Run (Regression Guard): uv run pytest backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/test_blueprint_sdui_crash.py -v</action>
    <action>Verify: MyPy strict passes with zero new # type: ignore annotations.</action>
    <action>Verify: All existing blueprint tests still pass — no regressions from the dispatch table migration or circular imports.</action>
  </step>

  <validation_gate>
    <check>grep_search for "from collections.abc import Callable" at module level (NOT inside __init__) in @[c:\src\quorum\backend_v2\services\blueprint.py]</check>
    <check>grep_search for "Callable[[AdapterContext]" in @[c:\src\quorum\backend_v2\services\blueprint.py] — confirms new type signature</check>
    <check>grep_search for "Callable[..." (old signature) in @[c:\src\quorum\backend_v2\services\blueprint.py] — MUST return zero results</check>
    <check>grep_search for "class AdapterContext" in @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]</check>
    <check>grep_search for "extra=\"forbid\"" in @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]</check>
    <check>grep_search for "mcp_audit_map=mcp_audit_data" in @[c:\src\quorum\backend_v2\services\blueprint.py] — confirms naming bridge</check>
    <check>Run: uv run python scripts/backend_audit_loop.py backend_v2 --test</check>
  </validation_gate>
</execution_protocol>
```
