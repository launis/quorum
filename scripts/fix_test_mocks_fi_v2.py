import os
import re


def fix_mocks(path):
    # Match JSON-style dict where "translations": {"en": <ANYTHING_EXCEPT_BRACE>}
    pattern1 = re.compile(r'({"default_locale":\s*["\']en["\'],\s*"translations":\s*{["\']en["\']:\s*([^}]+))(})')
    # Match kwargs-style dict
    pattern2 = re.compile(r'(translations\s*=\s*{\s*["\']en["\']:\s*([^}]+))(})')

    if os.path.isfile(path):
        files = [path]
    else:
        files = []
        for root, _, fs in os.walk(path):
            for f in fs:
                if f.endswith('.py'):
                    files.append(os.path.join(root, f))

    for file in files:
        with open(file, encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # We need to make sure we don't accidentally match something that already has "fi"
        def repl(m):
            g1 = m.group(1)
            g2 = m.group(2)
            if '"fi"' in g1 or "'fi'" in g1:
                return m.group(0)
            return f'{g1}, "fi": {g2.strip()}' + m.group(3)

        content = pattern1.sub(repl, content)
        content = pattern2.sub(repl, content)

        if content != original_content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f"Fixed {file}")

if __name__ == "__main__":
    fix_mocks('c:/src/quorum/backend_v2/tests')
    fix_mocks('c:/src/quorum/backend_v2/llm/mock_data.py')
