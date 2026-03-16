import glob

for filepath in glob.glob("backend/models/domain/*.py"):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if "strict=False" in content:
        content = content.replace("strict=False", "strict=True")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
