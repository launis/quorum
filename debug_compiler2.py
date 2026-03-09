import json
import traceback
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

db = json.load(open('c:/src/quorum/data/db_v2.json', encoding='utf-8'))
mat = next((m for m in db['matrices'].values() if m.get('id') == 'matrix_input_processing'), None)
pc = PromptCompiler()

# Temporarily copy logic from the file directly to avoid the AppException mask
schema_name = "Test"
criteria = [mat]

from pydantic import BaseModel, Field, create_model

fields = {}
for crit in criteria:
    if crit.get("type") == "instruction":
        continue

    crit_id = crit.get("id")
    label_obj = crit.get("label")
    label = pc.resolve_i18n(label_obj, "en") if label_obj else crit_id
    
    desc_obj = crit.get("description")
    base_desc = pc.resolve_i18n(desc_obj, "en") if desc_obj else f"Evaluation for {label}"

    value_type = float if crit.get("allow_decimals", False) else int

    fields[crit_id] = (
        value_type,
        Field(..., description=f"{label}: {base_desc}")
    )

if not fields:
    fields["_acknowledged"] = (
        str,
        Field(default="yes", description="Acknowledge completion of the instruction.")
    )

print("Fields going to Pydantic:", fields)
DynamicModel = create_model(schema_name, **fields)
print("SUCCESS:", DynamicModel)
