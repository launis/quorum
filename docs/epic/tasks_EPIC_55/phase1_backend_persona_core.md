# Phase 1: Backend Core-Injection (Architecture)

## Source
Epic Phase 1, Steps 1-4

## Context
- `backend_v2/engine/prompt_compiler.py` (CONTEXT)

## Targets
- `backend_v2/core/system_directives.py` (TARGET - New)
- `backend_v2/core/v2_core.py` (TARGET)
- `backend_v2/engine/prompt_compiler.py` (TARGET)
- `docs/architecture/01_engine_architecture.md` (TARGET)

## Architectural Laws
- **Rule 05 - naked_prompt_injection**: All dynamic prompt insertions MUST be wrapped in explicit XML tags. When PromptCompiler injects the persona, it must wrap it in `<global_framework>` or similar tags.
- **Rule 05 - hybrid_prompting_mandate**: All system prompts MUST use XML tags inside Markdown.
- **Rule 00 - the_zero_compromise_pledge**: Pydantic schemas must be strict. `ExecutionPersona` must be validated. No fallback values if it's missing in DB unless a default is strictly defined.

## Implementation Steps
1. **Module Creation**: Create `backend_v2/core/system_directives.py`. Define an Enum `ExecutionPersona` (e.g., `DETERMINISTIC_PARSER`, `GENERATIVE_ASSISTANT`, `IRRELEVANT_FALLBACK`). 
2. **Constant Definition**: In `system_directives.py`, define the constant strings for each persona (e.g., `DETERMINISTIC_PARSER_FRAMEWORK` string containing the Zero-Interpretation rules).
3. **Pydantic Model Update**: Modify `backend_v2/core/v2_core.py`. Import `ExecutionPersona` and update the `PromptBlock` Pydantic model to include `execution_persona: ExecutionPersona = Field(default=ExecutionPersona.DETERMINISTIC_PARSER)`.
4. **Prompt Compiler Update**: Modify `backend_v2/engine/prompt_compiler.py`. Update `compile_xml_rubrics` to read `block.execution_persona` and fetch the static framework from `system_directives.py`. Wrap this string in explicit XML tags (e.g. `<execution_persona_framework>`) and prepend it to the LLM system prompt.
5. **Documentation**: Update `docs/architecture/01_engine_architecture.md` to reflect the new SSOT Persona Injection architecture.

## Testing & Quality Gate Plan
- **Unit Tests**: Update `tests/unit/test_prompt_compiler.py` to verify that `ExecutionPersona` correctly injects the correct string with XML boundaries.
- **Quality Gate**: Run `uv run python scripts/backend_audit_loop.py backend_v2/core/v2_core.py backend_v2/engine/prompt_compiler.py --test`
