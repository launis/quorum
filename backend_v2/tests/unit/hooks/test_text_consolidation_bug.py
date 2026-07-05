from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def test_synthesis_caching_bug_repro():
    # Simulate text_consolidation_hook message formatting
    raw_input_text = "This is a very long synthesis context..."

    # We removed execution_parameters from build_system_directive
    sys_prompt = "## Objective\nSynthesize."

    # We explicitly add the tag to user_content
    exec_params_xml = "<execution_parameters>\n<max_extension_items>5</max_extension_items>\n</execution_parameters>"
    user_content = raw_input_text.strip()
    user_content += f"\n\n{exec_params_xml}"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_content},
    ]

    compiler = PromptCompilerAdapter()
    compiled_prompt = compiler.compile_prompt(messages)

    dynamic_msgs = compiled_prompt.to_dynamic_flat()

    # Now dynamic_msgs should NOT be empty! It should contain the <execution_parameters>
    assert len(dynamic_msgs) > 0, (
        "Dynamic messages are empty! This will cause LiteLLM Warning and crash the generation."
    )

    # And the static messages should contain the raw_input_text!
    static_msgs = compiled_prompt.to_static_flat()
    assert "very long synthesis context" in static_msgs[1]["content"]
