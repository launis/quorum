import pathlib
import re

f = pathlib.Path('backend_v2/tests/unit/test_night_shift_hardener.py')
code = f.read_text('utf-8')

# We find ALL instances of the inline `return MockResponse(...) if ... else MockResponse(...)`
pattern = r'(\s*)return MockResponse\(json\.dumps\(\{"hardened_code": __import__\("json"\)\.loads\(json_data\)\.get\("hardened_code", ""\)\}\)\) if getattr\(kwargs\.get\("response_format"\), "__name__", ""\) == "HealingResponse" else MockResponse\(json_data\)'

replacement = r'''\1is_healing = getattr(kwargs.get("response_format"), "__name__", "") == "HealingResponse"
\1if is_healing:
\1    return MockResponse(
\1        json.dumps({"hardened_code": __import__("json").loads(json_data).get("hardened_code", "")})
\1    )
\1return MockResponse(json_data)'''

code = re.sub(pattern, replacement, code)

# We also still have 5 long lines left for JudgeResponse! Wait, the JudgeResponse ones were successfully replaced?
# The error list:
# 84, 136, 178, 359, 411 are all the `HealingResponse` inline returns!
# 125, 165, 238, 319, 378 are the `JudgeResponse` lines! Wait!
# Let me check my previous script. My previous script ONLY replaced `            return MockResponse(...)`!
# So if it was indented differently (like 16 spaces), it skipped it!

judge_pattern = r'(\s*)return MockResponse\(json\.dumps\(\{"chain_of_thought": "Looks good", "is_approved": True, "rejection_reason": ""\}\)\)'
judge_replacement = r'''\1return MockResponse(
\1    json.dumps({"chain_of_thought": "Looks good", "is_approved": True, "rejection_reason": ""})
\1)'''

code = re.sub(judge_pattern, judge_replacement, code)

f.write_text(code, 'utf-8')
print("Kaikki Ruff E501 virheet korjattu regexillä.")
