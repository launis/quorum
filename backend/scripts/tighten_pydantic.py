import os
import re

backend_dir = r"c:\src\quorum\backend"

# Files to skip or handle specially
skip_files = [
    r"c:\src\quorum\backend\models\domain\xai.py",  # Handled manually due to dynamic judge keys
    r"c:\src\quorum\backend\api\schemas.py",
    r"c:\src\quorum\backend\tests\output\results.xml",
]

def map_config(match):
    # This function will replace extra="ignore" or frozen=True
    # but we want to turn them into strict models.
    # We will just replace extra="ignore", strict=True and frozen=True
    # with `frozen=True, strict=True`.

    # We want to replace the whole ConfigDict line
    pass

for root, _, files in os.walk(backend_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            if path in skip_files:
                continue

            with open(path, encoding="utf-8") as f:
                content = f.read()

            if "ConfigDict" in content:
                # We want to replace `extra="ignore"` -> `strict=True`
                # or `frozen=True` -> `frozen=True`

                # We have to be careful not to break non-domain files if they need it,
                # but let's just replace extra="ignore" with strict=True
                # and frozen=True with frozen=True

                new_content = re.sub(r'extra\s*=\s*["\']ignore["\']', "strict=True", content)
                new_content = re.sub(r'extra\s*=\s*["\']allow["\']', "strict=True", content)
                new_content = re.sub(r'frozen\s*=\s*False', "frozen=True", new_content)

                # Cleanup potential duplicates like `strict=True`
                new_content = re.sub(r'strict=True,\s*strict=True', "strict=True", new_content)
                new_content = re.sub(r'frozen=True,\s*frozen=True', "frozen=True", new_content)

                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {path}")
