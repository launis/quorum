import os
import re
from pathlib import Path

def refactor_fstrings(content):
    def repl(m):
        level = m.group(1)
        fstring_content = m.group(2)
        rest = m.group(3)
        
        parts = re.split(r'\{([^}]+)\}', fstring_content)
        new_string_parts = []
        vars_extracted = []
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                new_string_parts.append(part.replace('%', '%%'))
            else:
                new_string_parts.append('%s')
                var_expr = part.split(':')[0]
                vars_extracted.append(var_expr)
        
        new_string = "".join(new_string_parts)
        vars_str = ", ".join(vars_extracted)
        
        if vars_str:
            if rest.strip() == ')':
                return f'logger.{level}("{new_string}", {vars_str})'
            else:
                # Add a comma separator correctly
                clean_rest = rest.lstrip()
                if clean_rest.startswith(','):
                    return f'logger.{level}("{new_string}", {vars_str}{rest}'
                else:
                    return f'logger.{level}("{new_string}", {vars_str}, {rest}'
        else:
            return f'logger.{level}("{new_string}"{rest}'

    # re.DOTALL is important so .*? can span across newlines (e.g. exc_info=True on next line)
    pattern = r'logger\.(debug|info|warning|error|critical)\(\s*f"([^"]+)"(.*?\))'
    return re.sub(pattern, repl, content, flags=re.DOTALL)

def main():
    services_dir = Path("c:/src/quorum/backend_v2/services")
    count = 0
    # Directory scanning
    for file_path in services_dir.glob("*.py"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = refactor_fstrings(content)
        
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Refactored logs structurally in: {file_path.name}")
            count += 1
            
    print(f"\nCompleted! Refactored {count} files.")

if __name__ == "__main__":
    main()
