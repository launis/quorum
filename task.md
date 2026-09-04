# Task Tracking: Expanding SDUI Parity Testing to Structured Presentation & Stylistic Formatting

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_e2e_sdui_parity_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\8cef95ff-2665-4be3-a6a9-a03e585831be\implementation_plan.md]

## Execution Tasks
- [x] **Step 1: PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP & PARITY HARNESS PREPARATION**
  - [x] Replace sparse model imports in `backend_v2/tests/integration/test_sdui_semantic_parity.py#L21` with full concrete imports of all 17 SDUI block classes.
  - [x] Update `MatrixScorecardRowDTOFactory` in `test_sdui_semantic_parity.py#L59-L82` to set default `true_atoms: int | None = None` and `total_atoms: int | None = None`.
  - [x] Replace naked dicts/lists in `ReportDataDTOFactory` and `ScorecardAtomDTOFactory` with strictly typed defaults.
  - [x] Replace legacy `os`, `os.path`, `tempfile.mkstemp`, `os.close`, `os.remove` with `pathlib.Path` and `Path.unlink(missing_ok=True)`.
  - [x] Eradicate `hasattr` and `getattr` duck-typing violations in layout loop with strictly typed `match layout:` pattern matching.
  - [x] Clean up `client_app_v2/test/features/execution/sdui_semantic_parity_test.dart` (remove naked `print`, replace `throw Exception()` with `throw StateError()`, wrap test in `try...finally` for `semanticsHandle.dispose()`).
- [ ] **Step 2: FLUTTER SEMANTIC TOKEN EXTRACTOR ENHANCEMENT**
  - [ ] Implement granular typographical token extractor covering `RichText`, `Text`, and `SelectableText`.
  - [ ] Traverse `InlineSpan` hierarchy, cascading `TextStyle` to resolve effective `FontWeight` (`FontWeight.bold`, `w700`, `w800`, `w900`), `FontStyle.italic`, and `is_header` (`fontSize >= 20.0`).
  - [ ] Split multi-line spans by `\n`, filter accessibility states and noise tokens (<2 chars).
  - [ ] Emit structured JSON array `[{"text": String, "is_bold": bool, "is_italic": bool, "is_header": bool}]` to `DUMP_PATH`.
- [ ] **Step 3: PYTHON E2E PARITY ORCHESTRATOR MARKDOWN TOKEN VERIFIER**
  - [ ] Define strictly typed Pydantic V2 `SduiSemanticTokenDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
  - [ ] Deserialize tokens via `TypeAdapter(list[SduiSemanticTokenDTO])`.
  - [ ] Implement `verify_token_parity` (plain text, bold with negative lookaround / headers / table delimiter anchoring, italic with negative lookaround, headers in `#` lines).
  - [ ] Implement 4 ISTQB negative boundary partitions with collision-free candidate filtering.
- [ ] **Step 4: GOLDEN MASTER DOM & WIDGET STYLISTIC ASSERTION HARDENING**
  - [ ] In `backend_v2/tests/unit/test_sdui_template_parity.py`, add BeautifulSoup DOM tag/style assertions across SDUI blocks.
  - [ ] In `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart`, expand widget `TextStyle` assertions.
- [ ] **Step 5: PARITY TEST VERIFICATION & QUALITY GATES EXECUTION**
  - [ ] Run `uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py`.
  - [ ] Run `flutter test test/features/execution/views/widgets/sdui_golden_master_parity_test.dart`.
  - [ ] Run `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  - [ ] Run backend and flutter audit loops.
