# Phase 2B: Flutter StepRule Update & Seed Data Configuration

> **Source:** Epic 101, Phase 3 (Steps 2-6), Section 4 (Tripartite Configuration)

## Goal

Complete the cross-boundary `StepRule.engine_override` field synchronization between backend Pydantic and Flutter Freezed, update `seed_data.json` with engine override mappings and the new `"reasoning"` strategy, and implement the Vertex adapter logic for reasoning parameters.

## Architectural Invariants (Injected)

- `cross_language_enum_parity`: Backend enum → Flutter `@JsonEnum()` parity
- `frontend_feature_isolation`: StepRule model in `studio/models/workflow.dart`
- `silent_json_fallbacks` ban: `disallowUnrecognizedKeys: true` — new fields MUST be added to Freezed
- `database_schema_hallucination` ban: Do NOT restructure `seed_data.json` root arrays
- `global_config_sovereignty` (KI): Reasoning params in `seed_data.json` model_registry
- `unified_model_multiplexing` (KI): `LLMClient.from_strategy()` resolves strategy → model

## Dependencies

- **Phase 1A MUST be completed** (EngineOverrideStrategy enum exists).

---

## Milestone 2B.1: Flutter StepRule Freezed Update & Enum Parity

**Source: Epic Phase 3, Step 2 — Cross-Boundary MANDATORY Sub-Step**

### TARGET (Modify): [enums.dart](file:///c:/src/quorum/client_app_v2/lib/core/models/enums.dart)

First, define the `EngineOverrideStrategy` enum to satisfy the **cross_language_enum_parity** rule:

```dart
/// Execution strategy overrides for the engine.
@JsonEnum()
enum EngineOverrideStrategy {
  @JsonValue('PRE_HYDRATED_SYNTHESIS')
  preHydratedSynthesis,
  @JsonValue('DYNAMIC_TOOL_AGENT')
  dynamicToolAgent,
}
```

### TARGET (Modify): [workflow.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/workflow.dart)

Add `engine_override` field to the `StepRule` Freezed factory using the new enum:

```dart
@Freezed(equal: false)
abstract class StepRule with _$StepRule {
  const StepRule._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory StepRule({
    @StrictOpaqueIdConverter() required String id,
    @StrictOpaqueIdConverter() required String taskBlueprint,
    @Default([]) List<String> dependsOn,
    @Default({}) Map<String, String> inputMappings,
    @JsonKey(name: 'engine_override') EngineOverrideStrategy? engineOverride,  // NEW — strict enum mapping
    @Default(0.0) double uiPosX,
    @Default(0.0) double uiPosY,
  }) = _StepRule;

  factory StepRule.fromJson(Map<String, dynamic> json) =>
      _$StepRuleFromJson(json);
}
```

> **CRITICAL ARCHITECTURE RULE**: You MUST include `@JsonKey(name: 'engine_override')`! Because the model enforces `disallowUnrecognizedKeys: true`, if you omit the JsonKey, Dart will expect `engineOverride` (camelCase) and immediately crash when it receives the snake_case key from Python.

### TARGET (Run): Build Runner

After modifying the Freezed model, the execution agent MUST run:
```
cd client_app_v2; dart run build_runner build -d;
```

### CONTEXT (Read-Only):
- `backend_v2/models/v2_core.py` — Backend `StepRule` (already has `engine_override` from Phase 1A)

---

## Milestone 2B.1.5: UI Fallback Guarantee (AppExceptionBoundary)

**Source: Epic Phase 4 — System 2 Safeguards**

### TARGET (Modify): [app_error_boundary.dart](file:///c:/src/quorum/client_app_v2/lib/core/error/app_error_boundary.dart)

Update `AppExceptionBoundary` to safely intercept rendering errors caused by dynamically injected Virtual Steps. Because the Virtual Step has no corresponding definition in the Freezed model, it will throw an exception during rendering.

**CRITICAL RULE ENFORCEMENT**: According to the **Absolute Death / Diagnostic Node** mandate (Rule 02_flutter_desktop.md), we must **NOT** hide these errors with `SizedBox.shrink()` or a loading skeleton. 

1. Ensure that if `error.toString()` indicates a missing step definition (e.g., contains the dynamic `stp_` prefix, or explicitly mentions missing rules), it explicitly renders a localized red `Diagnostic Node`. Do not hide the error.
2. The UI must explicitly inform the user that a Virtual Step parsing failure occurred.


### CONTEXT (Read-Only):
- `client_app_v2/lib/core/error/app_error_boundary.dart` — Target file

---

## Milestone 2B.2: Seed Data — Map `engine_override` to Existing Steps

**Source: Epic Phase 3, Steps 4-5**

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

For each `StepRule` in the workflow's `steps` array:

1. **Analytical Steps** (Guard, Analyst, Logician, Overseer, etc.): Add `"engine_override": "PRE_HYDRATED_SYNTHESIS"`
2. **Tavily/MCP Steps** (Fact-Checker with `tool_id: "mcp_tavily_search"`): Set `"engine_override": "DYNAMIC_TOOL_AGENT"` to retain external internet access and `MCPAuditTrace`
3. **Logic Steps** (Rendering, Scoring): Leave `"engine_override": null` (default routing)

> **CRITICAL**: The execution agent MUST read the actual `seed_data.json` to identify which specific step IDs map to which categories. Do NOT hardcode step IDs in this plan — use the existing `task_blueprint` references and their associated `Step.type` / `tool_id` fields to make the determination.

### CONTEXT (Read-Only):
- `backend_v2/seed/seed_data.json` — Full workflow configuration

---

## Milestone 2B.3: Seed Data — Add `"reasoning"` Strategy to Model Registry

**Source: Epic Phase 3, Step 5 — Future-Proof Reasoning Configuration**

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

In the `model_registry` system config block, add a new `"reasoning"` strategy entry:

```json
{
  "strategy": "reasoning",
  "model": "gemini-2.5-pro",
  "provider": "vertex",
  "additional_params": {
    "thinking_budget_tokens": 2048
  }
}
```

### CONTEXT (Read-Only):
- `backend_v2/seed/seed_registry.py` — Validates `SystemConfigModelRegistry` schema

---

## Milestone 2B.3.5: FastDev Alias for Reasoning Strategy

**Source: Epic Phase 3, Step 5 — Local Development Optimization**

### TARGET (Modify): [settings.py](file:///c:/src/quorum/backend_v2/settings.py)

In `settings.py`, under the `strategy_aliases` property, add `"reasoning": "fast"` to ensure that the heavy `reasoning` strategy obeys the FastDev mode downgrade when running locally.

```python
    @computed_field  # type: ignore[prop-decorator]
    @property
    def strategy_aliases(self) -> dict[str, str]:
        """Neutral map for strategy rerouting in development."""
        if self.environment.lower() == "development" and self.dev_execution_mode == "fast":
            return {
                "strict_strategy": "fast",
                "evaluation_strategy": "fast",
                "test_strategy": "fast",
                "strict": "fast",
                "deep": "fast",
                "synthesis": "fast",
                "reasoning": "fast",  # NEW
            }
        return {}
```

### CONTEXT (Read-Only):
- `backend_v2/settings.py` — Settings configuration

---

## Milestone 2B.4: Vertex Adapter — Reasoning Parameter Extraction

**Source: Epic Phase 3, Step 5 — Adapter Implementation Mandate**

### TARGET (Modify): [vertex_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/vertex_adapter.py)

In the adapter's request preparation logic, implement dynamic extraction of reasoning parameters:

1. Check if `additional_params` (passed via the `config` argument) contains `"thinking_budget_tokens"` key
2. If present, extract the value and inject it into the `call_kwargs` dictionary for LiteLLM.
   > **CRITICAL ARCHITECTURE RULE**: Do NOT attempt to assign `generation_config.thinking_config`! `vertex_adapter.py` only modifies the `call_kwargs` dictionary sent to `litellm.acompletion`. There is no `generation_config` Python object.
   ```python
   if config and hasattr(config, "additional_params") and "thinking_budget_tokens" in config.additional_params:
       budget = config.additional_params.get("thinking_budget_tokens")
       if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
           call_kwargs["extra_body"] = {}
       
       # Use extra_body so Litellm passes it natively to Vertex SDK
       if "thinkingConfig" not in call_kwargs["extra_body"]:
           call_kwargs["extra_body"]["thinkingConfig"] = {}
       call_kwargs["extra_body"]["thinkingConfig"]["thinkingBudgetTokens"] = int(budget)
   ```
3. **Provider Abstraction Mandate**: This logic MUST live exclusively in `vertex_adapter.py`. The global `LiteLLMProvider` / `provider.py` MUST NOT contain any Gemini-specific parameter mapping.

### CONTEXT (Read-Only):
- `backend_v2/llm/provider.py` — Global provider (must NOT be modified)
- `backend_v2/llm/adapters/base_adapter.py` — Base adapter interface

---

## Milestone 2B.5: Apply Reasoning Strategy to Critical Nodes in Seed Data

**Source: Epic Phase 3, Step 6**

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

Locate the most cognitively demanding steps (e.g., those with critical/deep analysis roles) and change their `model_strategy` to `"reasoning"`.

> **NOTE**: In Development Mode, Quorum automatically downgrades all strategies to "flash". The JSON configuration MUST still be completed perfectly for Production.

### CONTEXT (Read-Only):
- `backend_v2/seed/seed_data.json` — Same file, different section

---

## Milestone 2B.6: Cleanup Obsolete Opaque ID Prompts

**Source: Red-Team Discovery**

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

Locate all instances of the following obsolete instruction in `ai_description` fields:
`- Opaque Stripe IDs: All rule IDs are opaque 16-hex strings prefixed with tda_.`
(or similar wording that instructs the LLM to output `tda_` prefixes).

Remove these sentences entirely. They conflict with Epic 92 `AliasEngine`, which translates `tda_` UUIDs into semantic `a0` anchors before the LLM sees them. Leaving this instruction causes the LLM to hallucinate `tda_` prefixes or fail to find quotes because it doesn't understand the `a0` alias.

---

## Bidirectional Integration Check

| Consumer | Producer | Verified? |
|---|---|---|
| Flutter `StepRule` parses `engineOverride` from JSON | Backend emits it in API response | ✅ |
| `NodeExecutor` reads `step.engine_override` | `seed_data.json` populates it | ✅ |
| `LLMClient.from_strategy("reasoning", repo)` | `model_registry` defines it | ✅ |
| `VertexCacheAdapter` maps `thinking_budget_tokens` | `additional_params` in seed data | ✅ |

---

## Testing & Quality Gate Plan

### Flutter Quality Gate:
```
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/ --build
```

### Backend Quality Gate:
```
uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/vertex_adapter.py --test
uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test
```

### Seed Re-Seeding:
```
uv run python backend_v2/seed/run_seed.py local
```

### Unit Tests:
1. **`test_vertex_adapter_reasoning.py`** — Verify `thinking_budget_tokens` is extracted and mapped to `thinking_config`.
2. **`test_seed_data_engine_override.py`** — Validate all step rules in seed data have valid `engine_override` values or null.

---

## Session Handover
```
Achieved: Cross-boundary StepRule sync, seed data configuration, reasoning strategy, Vertex adapter.
Remaining: Phase 3+ (deferred — Tier 1 re-invocation needed).
```
