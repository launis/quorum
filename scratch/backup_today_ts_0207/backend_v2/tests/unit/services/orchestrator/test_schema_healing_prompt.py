from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_schema_healing_prompt_includes_atom_id_guidance() -> None:
    compiler = PromptCompiler()
    error_msg = """[{"type":"missing","loc":["evaluations",2,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["osoittavat"],"semantic_reasoning":"Lauseessa..."}}]"""

    prompt = compiler.get_schema_healing_prompt(error_msg=error_msg, is_logical_error=False, is_eof=False)

    assert "missing 'atom_id'" in prompt, "Healing prompt must specifically address missing atom_id"
    assert "REMOVE that evaluation block" in prompt, (
        "Healing prompt must instruct to drop hallucinated blocks without IDs"
    )
    assert "Do not hallucinate items" in prompt, "Healing prompt must forbid hallucinated items"
    print("Test Passed: Schema healing prompt is correctly hardened.")


def test_schema_healing_prompt_strictness_override() -> None:
    compiler = PromptCompiler()
    error_msg = "Extra inputs are not permitted"

    # strictness = 99 (no override)
    prompt_99 = compiler.get_schema_healing_prompt(
        error_msg=error_msg, is_logical_error=False, is_eof=False, strictness_level=99
    )
    assert "STRICTNESS OVERRIDE ACTIVE" not in prompt_99

    # strictness = 100 (override active)
    prompt_100 = compiler.get_schema_healing_prompt(
        error_msg=error_msg, is_logical_error=False, is_eof=False, strictness_level=100
    )
    assert "STRICTNESS OVERRIDE ACTIVE" in prompt_100
    assert "'contextual_override'" in prompt_100
    assert "'override_reason'" in prompt_100
    print("Test Passed: Schema healing prompt correctly handles strictness override.")
