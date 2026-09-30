> **STATUS: READY FOR EXECUTION / VALMIS TOTEUTUKSEEN**

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: SynthesisEngine Protocol Inheritance & Type Hardening (F-03)

## 1. Executive Summary & Problem Description

### Nykytila (Havainto F-03)
Quorumin suoritusmoottorit toteuttavat keskitetyn `ExecutionEngine(Protocol)` -rajapinnan (`@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`).
Koodikannassa kaksi moottoria periytyy suoraan protokollasta:
- `TDAEngine(ExecutionEngine)` (`@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`)
- `PromptEngine(ExecutionEngine)` (`@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`)

Kuitenkin `SynthesisEngine` (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`) ilmoittaa moduulitason docstringissään:
`"""Implements the ExecutionEngine protocol for LLM-driven synthesis processing."""`
mutta sen luokkamäärittely on pelkkä `class SynthesisEngine:` ilman eksplisiittistä `ExecutionEngine` -protokollaperiytymistä tai PEP 698 `@override` -annotaatioita.

Tämä jättää `SynthesisEngine`:n puhtaasti duck-typingin varaan, mikä rikkoo:
1. `ki_execution_engine_protocol.md` -periaatteen: Kaikkien moottoreiden tulee olla tyyppitarkastimelle (MyPy strict) eksplisiittisesti `ExecutionEngine` -yhteensopivia.
2. `01-python-backend.md` -säännön (`python_314_modern_syntax` ja PEP 698): Rajapintatoteutusten metodit on suojattava `@override`-annotaatiolla.
3. `ki_execution_engine_protocol.md` -säännön (`atomic_telemetry_signaling_mandate`): `SynthesisEngine` ei tällä hetkellä aseta `request.running_event` -signaalia semaforilukon sisällä, toisin kuin `PromptEngine` ja `TDAEngine`.

### Ajoitus: Tehdäänkö tämä ennen PostgreSQL-migraatiota?
**KYLLÄ, ehdottomasti ennen PostgreSQL-migraatiota.**
Perustelut:
1. **Nolla riippuvuutta pysyvyyskerrokseen:** `SynthesisEngine` on 100 % DAG-suoritusputken muistinsisäinen orkestrointikomponentti. Se ei lue eikä kirjoita tietokantaan, eikä sillä ole kytkentää TinyDB- tai PostgreSQL-malleihin.
2. **Minimaalinen blast radius:** Tehtävä käsittää tasan yhden tuotantotiedoston ja yhden testitiedoston täsmämuokkauksen.
3. **Pohjan vakauttaminen:** Suoritusputken tyyppipuhtaus on valmis ja testattu ennen kuin aloitetaan laajempi tietokantamigraatio.

---

## 2. Target Scope & Boundaries

### 2.1 Muokattavat tiedostot (Target Files)
- `[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`

### 2.2 Viite- ja lukutiedostot (Context / Read-Only Files)
- `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]` (SSOT `ExecutionEngine(Protocol)`)
- `@[backend_v2/services/orchestrator/engines/__init__.py]` (Moottorien julkiset vientisymbolit)
- `@[backend_v2/models/dtos/engine.py#L61-L132]` (`EngineExecutionRequest`)
- `@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` (`_resolve_execution_engine` palauttaa `ExecutionEngine`)
- `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` (`LLMNodeStrategy` suoritus)

---

## 3. Five-Axis System 2 Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` | Banned duck-typing without formal Protocol inheritance, missing PEP 698 `@override` on `execute()`, and omitted `running_event` telemetry signaling inside the semaphore lock. | Formal `class SynthesisEngine(ExecutionEngine):` inheritance with PEP 698 `@override` on `execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`, and atomic `if request.running_event: request.running_event.set()` signaling inside `async with request.semaphore_cm:`. | Pruned unnecessary wrapper classes, intermediate adapter layers, and speculative engine factories. Uses direct protocol inheritance from `ExecutionEngine`. | `issubclass(SynthesisEngine, ExecutionEngine)` is `True`; `isinstance(engine, ExecutionEngine)` is `True`; MyPy strict passes cleanly; `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test`. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` | Banned defensive `.get("error_code")` dict lookups in test assertions across error-handling tests and omitted ISTQB test coverage for Protocol subclassing, instance typing, and semaphore telemetry signaling. | Direct typed dictionary assertions `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value`, formal `issubclass` and `isinstance` Protocol verification, and dedicated negative partition tests for null concurrency limiters. | Pruned redundant mock classes or multi-layer test fixtures; reuses existing `base_request` fixture and `mock_executor` with typed `AsyncMock`. | `pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` passes 100% with >= 90% branch coverage (16/16 tests passing). |

---

## 4. Execution Protocol & Action Steps

<execution_protocol>
  <phase id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <step id="1.1" name="FIX_TEST_ASSERTION_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L108-L121]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L167-L180]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L183-L199]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == "CUSTOM_ERROR"` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L434-L453]`, add explicit `assert exc_info.value.details is not None` and `assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value` to enforce Fail-Fast schema assertions.</action>
    </step>
  </phase>

  <phase id="2" name="ENGINE_PROTOCOL_INHERITANCE_AND_OVERRIDE">
    <step id="2.1" name="INHERIT_EXECUTION_ENGINE_PROTOCOL">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, import `override` from `typing` and import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, update class definition to `class SynthesisEngine(ExecutionEngine):`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L286]`, decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    </step>
    <step id="2.2" name="ATOMIC_TELEMETRY_SIGNALING">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L286]`, signal `if request.running_event: request.running_event.set()` strictly inside `async with request.semaphore_cm:` immediately before dispatching `self._executor.execute_structured_task` per `ki_execution_engine_protocol.md`.</action>
    </step>
  </phase>

  <phase id="3" name="TEST_EXPANSION_AND_ISTQB_PARTITIONS">
    <step id="3.1" name="ADD_PROTOCOL_INHERITANCE_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and `ErrorCodes` from `backend_v2.exceptions`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_implements_protocol()` asserting `issubclass(SynthesisEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_signals_running_event()` asserting `running_event.is_set()` is True after execution with a provided `running_event`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_null_concurrency_guards()` asserting execution succeeds without error when `semaphore=None` and `running_event=None` to mathematically verify `request.semaphore_cm` nullcontext wrapping.</action>
    </step>
  </phase>

  <phase id="4" name="UNIVERSAL_QUALITY_GATE_VERIFICATION">
    <step id="4.1" name="RUN_BACKEND_AUDIT_LOOP">
      <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test` to verify Ruff formatting, MyPy strict typecheck, AST guardrails, and Pytest coverage.</action>
      <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Synthesis_Engine_Protocol_Inheritance.md` to verify markdown boundaries and table-protocol parity.</action>
    </step>
  </phase>
</execution_protocol>

---

## 5. Falsification & Red-Teaming Matrix

| Risk ID | Hypothesized Failure Mode | Likelihood | Impact | Architectural Countermeasure & Falsification Anchor |
| :--- | :--- | :--- | :--- | :--- |
| **RISK-01** | `execute()` signature diverges from `ExecutionEngine.execute()` Protocol definition causing MyPy strict error under `@override`. | Low | High | Signature parity verified: both require `(self, request: EngineExecutionRequest) -> EngineExecutionResult`. Verified by MyPy strict in `backend_audit_loop.py`. |
| **RISK-02** | `running_event.set()` called prematurely outside the acquired semaphore lock, misreporting queued state as active running state. | Medium | High | Explicit mandate: `if request.running_event: request.running_event.set()` MUST reside strictly inside `async with request.semaphore_cm:`. Verified by `test_synthesis_engine_signals_running_event`. |
| **RISK-03** | Test assertion `.get("error_code")` silently passes with `None` if error dictionary structure changes. | Low | Medium | Pre-implementation cleanup replaces `.get("error_code")` across all 3 test functions with direct subscript `details["error_code"]`, enforcing Fail-Fast `KeyError` if schema deviates. |
| **RISK-04** | Runtime `issubclass(SynthesisEngine, ExecutionEngine)` fails if `ExecutionEngine` is not `@runtime_checkable` or not a direct base. | Low | Critical | `ExecutionEngine` is decorated with `@runtime_checkable` in `base.py`, and `SynthesisEngine` explicitly declares `class SynthesisEngine(ExecutionEngine):`. Verified by `test_synthesis_engine_implements_protocol`. |
| **RISK-05** | Null concurrency limiters crash with `AttributeError` when `semaphore=None` or `running_event=None`. | Low | High | `request.semaphore_cm` natively wraps null semaphores in `contextlib.nullcontext()`, and `running_event` is guarded by an explicit null check before calling `.set()`. Verified by `test_synthesis_engine_null_concurrency_guards`. |

---

## 6. Matemaattiset Laatuportit & Verifiointi

Toteutuksen jälkeen ajetaan Quorumin pakollinen backend-auditointi:

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test
```

### Hyväksyntäkriteerit:
1. `issubclass(SynthesisEngine, ExecutionEngine)` palauttaa `True`.
2. `isinstance(engine, ExecutionEngine)` palauttaa `True`.
3. MyPy strict tarkistaa `@override`-dekoraattorin ja signatuurin 100 % virheettömästi ilman tyyppirikkoutumisia.
4. `test_synthesis_engine.py` ja `test_prompt_engine.py` menevät läpi 100 % (vähintään 16 testiä `test_synthesis_engine.py`:ssa, kattavuus >= 90 %).
5. `audit_markdown_boundaries.py` läpäisee suunnitelman 0 virheellä (MBD001-MBD009).


