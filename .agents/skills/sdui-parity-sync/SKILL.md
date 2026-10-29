---
name: sdui-parity-sync
description: Enforce 1:1 Cross-Domain DTO, Jinja PDF, and Flutter Freezed SDUI semantic parity whenever modifying SDUI models, adapters, PDF templates, or Flutter SDUI widgets.
---

# Quorum Skill: Cross-Domain SDUI, PDF & DTO Semantic Parity (`sdui-parity-sync`)

<system_prompt>
  <objective>Guarantee 100% mathematical and semantic parity across Backend Python Pydantic V2 DTOs, Backend SDUI Adapters, Jinja2 PDF Templates, and Frontend Dart 3 Freezed models &amp; Dumb Painter SDUI widgets.</objective>
  <role>Principal Cross-Domain SDUI &amp; Contract Parity Architect</role>

  <domain_boundary>
    <role>SDUI &amp; DTO CONTRACT SYNCHRONIZER</role>
    <instruction>Activate this skill automatically whenever creating, modifying, or auditing any file in `@[backend_v2/models/view/sdui.py]`, `backend_v2/models/dtos/`, `backend_v2/services/sdui/`, `@[backend_v2/services/pdf_generator.py]`, `backend_v2/templates/`, `@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`, or `client_app_v2/lib/features/execution/`.</instruction>
  </domain_boundary>

  <architectural_invariants>
    <rule_block id="tripartite_sdui_coupling_mandate">
      <mandate>Backend Python DTOs (`backend_v2/models/dtos/`, `@[backend_v2/models/view/sdui.py]`), Jinja PDF templates (`backend_v2/templates/`, `@[backend_v2/services/pdf_generator.py]`), and Frontend Dart Freezed models (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`, `client_app_v2/lib/features/execution/models/`) are mathematically coupled. "Deferred Parity" is STRICTLY FORBIDDEN: any field or block variant added, renamed, or removed in Python MUST be synchronously updated in Dart Freezed and Jinja PDF templates in the same plan.</mandate>
    </rule_block>

    <rule_block id="strict_serialization_contract">
      <mandate>Python SDUI blocks and DTOs MUST enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` with PEP 593 `Annotated` fields and `snake_case` naming. Dart Freezed models MUST enforce `@freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)` with `@JsonKey(name: 'snake_case')` mapping to camelCase Dart properties.</mandate>
    </rule_block>

    <rule_block id="dumb_painter_ui_boundary">
      <mandate>Flutter SDUI widgets (`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`) MUST act strictly as passive dumb painters wrapped in `AppErrorBoundary`, with zero semantic calculation logic, zero `SizedBox.shrink()` silent error masking, and 100% Theme Sovereignty (`Theme.of(context)` / `AppSemanticColors`).</mandate>
    </rule_block>
  </architectural_invariants>

  <execution_protocol>
    <step id="1" name="LOAD DOMAIN RULES">
      <action>Use `view_file` to load `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/01-python-backend.md]`, and `@[.agents/rules/02_flutter_desktop.md]`.</action>
    </step>

    <step id="2" name="SYNCHRONIZE TRIPARTITE CONTRACTS">
      <action>Verify 1:1 field name, type, discriminator, and nullability alignment across:
        1. Python Pydantic V2 schema (`@[backend_v2/models/view/sdui.py]` or `backend_v2/models/dtos/`)
        2. Python SDUI adapter (`backend_v2/services/sdui/adapters/`) and PDF renderer (`@[backend_v2/services/pdf_generator.py]`)
        3. Dart Freezed schema (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]` or feature model) and `build_runner` generated `.freezed.dart` / `.g.dart` artifacts
        4. Cross-language enums (`@[backend_v2/models/enums.py]` and `@[client_app_v2/lib/core/models/enums.dart]`)
      </action>
    </step>

    <step id="3" name="EXECUTE MANDATORY 4-GATE PARITY VERIFICATION">
      <action>Run all 4 deterministic verification gates sequentially via `run_command` before committing:
        1. **Cross-Domain DTO Parity Gate:**
           ```powershell
           $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch
           ```
        2. **SDUI &amp; PDF Semantic Parity Integration Gate:**
           ```powershell
           $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
           ```
        3. **Backend Audit Loop (Strict AST &amp; Unit Tests):**
           ```powershell
           $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <modified_backend_path> --test --ast-strict
           ```
        4. **Flutter Audit Loop (with Freezed Code Generation):**
           ```powershell
           $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<modified_flutter_path> --build
           ```
      </action>
    </step>
  </execution_protocol>
</system_prompt>

