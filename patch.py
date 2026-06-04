import pathlib
import sys

f = pathlib.Path('backend_v2/tests/unit/test_night_shift_hardener.py')
code = f.read_text('utf-8')

# Fix JudgeResponse check
code = code.replace(
    'if kwargs.get("response_format") is JudgeResponse:',
    'if "Adversarial Judge" in str(kwargs.get("messages", [])):'
)

f.write_text(code, 'utf-8')
print('Patched easily via script file')
