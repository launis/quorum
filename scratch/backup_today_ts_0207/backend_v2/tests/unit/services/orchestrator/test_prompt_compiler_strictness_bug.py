from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_prompt_compiler_build_dynamic_schema_accepts_strictness_level() -> None:
    """Reproduces the bug where PromptCompiler.build_dynamic_schema throws TypeError
    due to missing strictness_level parameter, which is passed by ChunkWorker.process_chunk.
    """
    compiler = PromptCompiler()

    # This should raise a TypeError since the signature is missing strictness_level
    compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[],
        has_search_result=False,
        has_shuffled_atoms=False,
        target_locale="en",
        strictness_level=100,
    )
