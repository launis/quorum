import os
import re

def refactor_loggers(directory):
    pattern1 = re.compile(r'logger\.error\(f"\[([A-Za-z0-9]+)\] \{ErrorCodes\.([A-Z_]+)\.name\}: \{msg\}"\)')
    pattern2 = re.compile(r'logger\.error\(f"\[([A-Za-z0-9]+)\] \{ErrorCodes\.([A-Z_]+)\.name\}: \{msg\}", exc_info=True\)')
    
    pattern3 = re.compile(r'logger\.warning\(f"\[([A-Za-z0-9]+)\] \{ErrorCodes\.([A-Z_]+)\.name\}: \{msg\}"\)')
    pattern4 = re.compile(r'logger\.warning\(f"\[([A-Za-z0-9]+)\] \{ErrorCodes\.([A-Z_]+)\.name\}: \{msg\}", exc_info=True\)')

    def config_replacer(match):
        inner = match.group(1)
        if "extra=" not in inner:
            if inner.strip():
                return f'ConfigDict({inner}, extra="forbid")'
            else:
                return 'ConfigDict(extra="forbid")'
        return match.group(0)

    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                original = content
                
                content = pattern1.sub(r'logger.error("[\1] %s: %s", ErrorCodes.\2.name, msg)', content)
                content = pattern2.sub(r'logger.error("[\1] %s: %s", ErrorCodes.\2.name, msg, exc_info=True)', content)
                content = pattern3.sub(r'logger.warning("[\1] %s: %s", ErrorCodes.\2.name, msg)', content)
                content = pattern4.sub(r'logger.warning("[\1] %s: %s", ErrorCodes.\2.name, msg, exc_info=True)', content)

                content = re.sub(r'ConfigDict\((.*?)\)', config_replacer, content)

                if original != content:
                    print(f"Refactored: {path}")
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(content)

if __name__ == "__main__":
    refactor_loggers(r"c:\src\quorum\backend_v2\models")
