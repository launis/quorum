from unittest.mock import AsyncMock
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


def test_chat_parser_caching_bug_repro():
    """Testaa, ett chat_parserin LLM-kutsun viestit ptyvt
    tyhjksi dynaamiseksi listaksi ilman <execution_parameters>-tgi.
    """
    raw_paste = "user: hei\nai: mita kuuluu?"

    # Tm on tsmlleen sama rakenne kuin chat_parser.py rivill 98
    messages = [
        {"role": "system", "content": "You are a data-mining expert."},
        {
            "role": "user",
            "content": (
                "<context>\nHere is the raw text to process:\n</context>\n"
                f"<source_data>\n{raw_paste}\n</source_data>\n"
                "<execution_parameters>\n<parsing_mode>strict</parsing_mode>\n</execution_parameters>"
            ),
        },
    ]

    compiler = PromptCompilerAdapter()
    compiled_prompt = compiler.compile_prompt(messages)

    dynamic_msgs = compiled_prompt.to_dynamic_flat()

    # Testin pitisi kaatua (AssertionError) jos data j tyhjksi,
    # kosk oikean ohjelman pitisi nimenomaan est tm.
    assert len(dynamic_msgs) > 0, (
        "CRITICAL BUG: Dynamic messages are empty! Vertex AI 400 Bad Request if PromptCache enabled."
    )
