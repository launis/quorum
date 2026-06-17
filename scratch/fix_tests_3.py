import re
import subprocess

# 1. test_synthesis_happy_path.py
path = r'c:\src\quorum\backend_v2\tests\unit\hooks\test_synthesis_happy_path.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("synthesized_markdown='Happy summary'", "content_blocks=[{'type': 'markdown', 'content': 'Happy summary'}]")
content = content.replace("synthesized_markdown='Negative'", "content_blocks=[{'type': 'markdown', 'content': 'Negative'}]")
content = content.replace("synthesized_markdown=", "content_blocks=")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. test_best_of_three.py
path = r'c:\src\quorum\backend_v2\tests\unit\services\orchestrator\strategies\llm_execution\test_best_of_three.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("assert resolved['evaluations'][0]['exact_quote'] == 'q'", "assert resolved['evaluations'][0]['exact_quote'] == ['q']")
content = content.replace("exact_quote='q'", "exact_quotes=['q']")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. test_chunk_worker.py
path = r'c:\src\quorum\backend_v2\tests\unit\services\orchestrator\strategies\llm_execution\test_chunk_worker.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("exact_quote='Valid quote'", "exact_quote=['Valid quote']")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 4. test_context_builder.py
path = r'c:\src\quorum\backend_v2\tests\unit\services\orchestrator\strategies\llm_execution\test_context_builder.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("assert ev['exact_quote'] == 'important evidence'", "assert ev['exact_quote'] == ['important evidence']")
content = content.replace("assert ev['exact_quote'] == 'Tämä on kriittinen lainaus dokumentista.'", "assert ev['exact_quote'] == ['Tämä on kriittinen lainaus dokumentista.']")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 5. test_prompt_compiler.py
path = r'c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_prompt_compiler.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("'exact_quote MUST be empty if True'", "'exact_quotes MUST be empty if True'")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished quick replacements")
