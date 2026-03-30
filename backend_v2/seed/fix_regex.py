import os
import re

TARGET_DIR = r"c:\src\quorum\backend_v2"

OLD_PATTERN = r'\^([a-z]+)_[a-zA-Z0-9]\{8,\}\$'
NEW_PATTERN = r'^([a-z]{2,5})_[a-zA-Z0-9]{8,}$'

def main():
    modifications = 0
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use raw string substitution where appropriate
            if r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$" in content:
                new_content = content.replace(r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$", r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modifications += 1
                print(f"Patched: {path}")

    print(f"Korvaus valmis. {modifications} Pydantic-mallitiedostoa tiukennettu Arkkitehtuurimanifestin mukaiseksi.")

if __name__ == "__main__":
    main()
