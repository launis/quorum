import pathlib

def fix_night_shift():
    f = pathlib.Path('backend_v2/tests/unit/test_night_shift_hardener.py')
    code = f.read_text('utf-8')
    
    # Fix 1: JudgeResponse line length
    code = code.replace(
        '            return MockResponse(json.dumps({"chain_of_thought": "Looks good", "is_approved": True, "rejection_reason": ""}))',
        '            return MockResponse(\n                json.dumps({"chain_of_thought": "Looks good", "is_approved": True, "rejection_reason": ""})\n            )'
    )
    
    # Fix 2: HealingResponse inline if line length
    old_inline = 'return MockResponse(json.dumps({"hardened_code": __import__("json").loads(json_data).get("hardened_code", "")})) if getattr(kwargs.get("response_format"), "__name__", "") == "HealingResponse" else MockResponse(json_data)'
    new_blocks = '''is_healing = getattr(kwargs.get("response_format"), "__name__", "") == "HealingResponse"
            if is_healing:
                return MockResponse(
                    json.dumps({"hardened_code": __import__("json").loads(json_data).get("hardened_code", "")})
                )
            return MockResponse(json_data)'''
    
    code = code.replace('            ' + old_inline, '            ' + new_blocks)
    
    f.write_text(code, 'utf-8')

def fix_structured_retry():
    f = pathlib.Path('backend_v2/tests/unit/llm/test_structured_retry.py')
    code = f.read_text('utf-8')
    
    old_line = '                messages=[{"role": "user", "content": "Execute! This is a long enough payload to pass the fail-fast check"}],'
    new_line = '                messages=[\n                    {"role": "user", "content": "Execute! This is a long enough payload to pass the fail-fast check"}\n                ],'
    
    code = code.replace(old_line, new_line)
    f.write_text(code, 'utf-8')

if __name__ == '__main__':
    fix_night_shift()
    fix_structured_retry()
    print("Ruff-virheet korjattu onnistuneesti.")
