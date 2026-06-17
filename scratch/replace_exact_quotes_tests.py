import os
import re


def replace_in_tests(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Replace exact_quote: ... = ... in Dataclasses / classes
                content = re.sub(r'exact_quote:\s*str\s*\|\s*None', r'exact_quotes: list[str] | None', content)
                content = re.sub(r'exact_quote:\s*str\s*=', r'exact_quotes: list[str] =', content)

                # Dictionary exact_quote assignments
                content = re.sub(r'"exact_quote":\s*"([^"]*)"', r'"exact_quotes": ["\1"]', content)
                content = re.sub(r"'exact_quote':\s*'([^']*)'", r"'exact_quotes': ['\1']", content)
                content = re.sub(r'"exact_quote":\s*""', r'"exact_quotes": []', content)
                content = re.sub(r"'exact_quote':\s*''", r"'exact_quotes': []", content)

                # Object creation kwargs
                content = re.sub(r'exact_quote="([^"]*)"', r'exact_quotes=["\1"]', content)
                content = re.sub(r"exact_quote='([^']*)'", r"exact_quotes=['\1']", content)

                # None checks & assignments
                content = re.sub(r'\.exact_quote\s*is\s*None', r'.exact_quotes == []', content)
                content = re.sub(r'\.exact_quote\s*==\s*None', r'.exact_quotes == []', content)
                content = re.sub(r'exact_quote\s*=\s*None', r'exact_quotes=[]', content)

                # Direct attribute access equality
                content = re.sub(r'\.exact_quote\s*==\s*"([^"]*)"', r'.exact_quotes == ["\1"]', content)
                content = re.sub(r'\.exact_quote\s*==\s*\'([^\']*)\'', r'.exact_quotes == [\'\1\']', content)

                # Accessing .exact_quote
                content = re.sub(r'\.exact_quote(?!\w)', r'.exact_quotes', content)

                # String literals mentioning exact_quote
                content = re.sub(r'"exact_quote"', r'"exact_quotes"', content)
                content = re.sub(r"'exact_quote'", r"'exact_quotes'", content)

                # Fix specific edge cases (like string matching in exception text if needed, but let's see)
                content = content.replace("exact_quotes cannot be '[CONTEXTUAL_OVERRIDE_APPLIED]'", "exact_quotes cannot contain '[CONTEXTUAL_OVERRIDE_APPLIED]'")

                if content != original:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated {file_path}")

if __name__ == "__main__":
    replace_in_tests(r"c:\src\quorum\backend_v2\tests")
