import os
import re

dump_file = r"C:\Users\risto\.gemini\antigravity-ide\brain\bb87cf3e-0f31-4b3f-85eb-6bb2bbfe5d5d\scratch\legacy_workflows_dump.txt"
workflows_dir = r"c:\src\quorum\.agents\workflows"

with open(dump_file, encoding="utf-8") as f:
    dump_text = f.read()

# Parse dump file into dictionary
legacy_files = {}
parts = dump_text.split("========================================")
i = 1
while i < len(parts):
    header = parts[i].strip()
    if header.startswith("FILE:"):
        fname = header.split("FILE:")[1].strip()
        content = parts[i+1].strip()
        legacy_files[fname] = content
        i += 2
    else:
        i += 1

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

report_path = r"C:\Users\risto\.gemini\antigravity-ide\brain\bb87cf3e-0f31-4b3f-85eb-6bb2bbfe5d5d\scratch\dropped_report.txt"
with open(report_path, "w", encoding="utf-8") as out:
    for fname, legacy_content in legacy_files.items():
        if legacy_content == "FILE DID NOT EXIST IN 2014e69b":
            continue

        current_path = os.path.join(workflows_dir, fname)
        if not os.path.exists(current_path):
            continue

        with open(current_path, encoding="utf-8") as f:
            current_content = f.read()

        current_norm = normalize(current_content)

        # Extract sentences from legacy (crude split by period or newline)
        # Specifically targeting instructions, e.g. <step> contents or bullet points
        sentences = re.split(r'[\.\n]', legacy_content)

        dropped = []
        for s in sentences:
            s = s.strip()
            if len(s) < 40:
                continue
            # If the normalized sentence is not in the normalized current content
            # (allow some slight mismatch by checking if 80% of words are found)
            words = [w for w in re.findall(r'[a-zA-Z0-9]{4,}', s.lower())]
            if not words: continue

            found_words = sum(1 for w in words if w in current_norm)
            if found_words / len(words) < 0.6:
                dropped.append(s)

        if dropped:
            out.write(f"\n--- POTENTIAL DROPPED CONTEXT IN {fname} ---\n")
            for d in dropped:
                out.write(f" - {d}\n")

print(f"Report written to {report_path}")
