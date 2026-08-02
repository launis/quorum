# Phase 3: Extract Penalties Adapter

**Overview:** Extract `_hydrate_penalties_block` from `blueprint.py` into a self-contained `PenaltiesAdapter` following the canonical KI template.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L113-L124] Phase 3

**Target Files:**
- @[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_penalties_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py] [MODIFY]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>blueprint.py contains ZERO direct AlertBlock instantiation for the penalties adapter.</item>
    <item>penalties_adapter.py is self-contained: it has its own module-level rules dictionary and strictly uses explicit Key-Access (RULES[key]) rather than .get().</item>
    <item>Atomic Test Migration: Any tests previously asserting on private methods are updated. (Note: No existing penalty tests found in test_blueprint.py, so only new tests are required).</item>
    <item>MyPy strict passes with zero new # type: ignore annotations.</item>
    <item>Zero bare except Exception: catch-alls in any adapter file.</item>
    <item>The word "Epic" (or "EPIC") does NOT appear in any added code, docstrings, or comments.</item>
    <item>Zero inline imports in any adapter file. All imports MUST be at the top of the file.</item>
    <item>The dispatch table _target_block_hydrators uses dict[str, Callable[[AdapterContext], list[AnySduiBlock]]] with uniform lambda-wrapped calling convention.</item>
  </dod_checklist>

  <anti_targets>
    <target>@[c:\src\quorum\backend_v2\services\blueprint.py] (Do not touch _hydrate_global_score_block, _hydrate_audit_trail_block, _hydrate_jargon_ratio_block)</target>
  </anti_targets>

  <step id="1" name="Read Canonical Patterns">
    <constraint invariant="knowledge_item_preflight">You MUST read KI `sdui_adapter_decomposition` (specifically `ki_sdui_adapter_pattern.md` in `appDataDir\knowledge\`) BEFORE creating the adapter file. The adapter MUST be structurally identical to the canonical reference template defined in the KI.</constraint>
    <action>Read @[C:\Users\risto\.gemini\antigravity-ide\knowledge\sdui_adapter_decomposition\artifacts\ki_sdui_adapter_pattern.md]</action>
  </step>

  <step id="2" name="Create Penalties Adapter">
    <action>Create @[c:\src\quorum\backend_v2\services\sdui\adapters\penalties_adapter.py] [NEW] with the exact two-section structure defined in the KI.</action>
    <action>Move the logic from `_hydrate_penalties_block` (currently at @[c:\src\quorum\backend_v2\services\blueprint.py#L788-L804]) into this new file.</action>
    <action>Section 1: AESTHETICS RULES MUST define a module-level dictionary (specifically `PENALTIES_RULES`) mapping a single key (specifically "default_penalty") to the visual properties (severity=VisualIntent.CRITICAL_OVERRIDE).</action>
    <constraint>Ensure strict typing and imports for `AnySduiBlock`, `AlertBlock`, and `VisualIntent`.</constraint>
    <constraint>MANDATE: You MUST remove the `.value` extraction from `VisualIntent.CRITICAL_OVERRIDE.value` that exists in the legacy code. The new adapter MUST pass the native `VisualIntent` Enum object to `AlertBlock` to comply with the `strict_enum_hydration_and_validation` rule.</constraint>
    <constraint>TESTING MANDATE: You MUST use a valid Pytest fixture for `AdapterContext` in `test_penalties_adapter.py` to provide the required fields (locale, execution, etc.) and avoid `ValidationError` crashes during test setup.</constraint>
    <contract_freeze>
      <signature>@staticmethod
def build(context: AdapterContext) -> list[AnySduiBlock]:</signature>
    </contract_freeze>
  </step>

  <step id="3" name="Modify Blueprint Dispatcher">
    <action>In @[c:\src\quorum\backend_v2\services\blueprint.py], import `PenaltiesAdapter` at the top of the file.</action>
    <action>Wire it into `_target_block_hydrators` in `BlueprintTransformer.__init__` (around line 107) replacing the `self._hydrate_penalties_block` reference with `lambda ctx: PenaltiesAdapter.build(ctx)`.</action>
    <demolish>
      REMOVE: existing `def _hydrate_penalties_block` method at @[c:\src\quorum\backend_v2\services\blueprint.py#L788-L804].
    </demolish>
  </step>

  <step id="4" name="Atomic Test Migration and Coverage">
    <action>Create new test file @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_penalties_adapter.py] [NEW].</action>
    <action>Check if any existing tests for `_hydrate_penalties_block` exist in @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py] (none were found by the planner, but verify anyway). If found, migrate them.</action>
    <action>Implement the mandatory test contracts.</action>
    <test_contracts>
      <test name="test_build_tampered_rules_dictionary_raises_keyerror" category="negative">
        <input>Mock PENALTIES_RULES to be empty {}</input>
        <expected>raises KeyError (verifies Fail-Fast dictionary access)</expected>
      </test>
      <test name="test_build_empty_list_returns_empty" category="boundary">
        <input>AdapterContext(penalties_applied=[])</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_valid_penalties_returns_alert_blocks" category="positive">
        <input>AdapterContext(penalties_applied=["Test Penalty"])</input>
        <expected>returns [AlertBlock(severity=VisualIntent.CRITICAL_OVERRIDE, text="Penalty applied: Test Penalty", ...)]</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <action>Run backend tests: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Run specific test: `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py`</action>
    <action>Verify zero bare `except Exception:` in `penalties_adapter.py` via `grep_search`.</action>
  </validation_gate>
</execution_protocol>
```
