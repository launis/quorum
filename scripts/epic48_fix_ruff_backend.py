import os
import re

# Fix anchor_validation_service.py (Trailing whitespaces on empty lines)
path = "backend_v2/services/orchestrator/anchor_validation_service.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if line.strip() == "" and len(line) > 1:
        lines[i] = "\n"
with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

# Fix atomizer.py
path = "backend_v2/services/orchestrator/atomizer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace(
    "# Usually, TDAAssertion schema enforces the field, so it might be empty string or missing if from raw JSON.",
    "# Usually, TDAAssertion schema enforces the field,\n                    # so it might be empty string or missing if from raw JSON."
)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix test_prompt_compiler.py
path = "backend_v2/tests/integration/test_prompt_compiler.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace(
    "evidence_found MUST be False and you must return an empty string \"\" for exact_quote. If rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation.",
    "evidence_found MUST be False and you must return an empty string \"\" for exact_quote. \\\nIf rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation."
)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix Scoring Engines
def fix_scoring_engine(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    old_line = "level_breakdown = {str(k): {\"hits\": v[\"hits\"], \"total\": v[\"total\"], \"dlqs\": v.get(\"dlqs\", 0)} for k, v in stats.items()}"
    new_line = "level_breakdown = {\n            str(k): {\"hits\": v[\"hits\"], \"total\": v[\"total\"], \"dlqs\": v.get(\"dlqs\", 0)}\n            for k, v in stats.items()\n        }"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

fix_scoring_engine("backend_v2/utils/scoring/average_engine.py")
fix_scoring_engine("backend_v2/utils/scoring/dampening_engine.py")
fix_scoring_engine("backend_v2/utils/scoring/waterfall_engine.py")

print("Ruff format issues fixed!")
