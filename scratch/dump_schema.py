import json
from backend_v2.services.orchestrator.schema_factory import SchemaFactory
from backend_v2.models.v2_core import PromptBlock

with open("data/db_v2.json", "r", encoding="utf-8") as f:
    db = json.load(f)

blueprint = None
blocks_dict = {}

for table in db.values():
    if isinstance(table, dict):
        for k, v in table.items():
            if isinstance(v, dict):
                if v.get("id") == "sp_ddb7cf7c8a0245d4":
                    blueprint = v
                elif v.get("id", "").startswith("blk_"):
                    blocks_dict[v["id"]] = v

criteria_blocks = []
for bid in blueprint.get("criteria_block_ids", []):
    block_data = blocks_dict.get(bid)
    if block_data:
        criteria_blocks.append(PromptBlock(**block_data))

factory = SchemaFactory(resolve_i18n_fn=lambda x, y: "test")
model = factory._build_dynamic_schema_internal(
    schema_name="Step_sr_0f7947ec7007498c_Response",
    has_search_result=False,
    has_shuffled_atoms=True,
    target_locale="en",
    strictness_level=100,
    criteria=criteria_blocks,
    cache_key="test_key",
    source_document_ids=["src_0", "src_1", "src_2"]
)

schema = model.model_json_schema()

def check_arrays(obj, path=""):
    missing = []
    if isinstance(obj, dict):
        if obj.get("type") == "array" and "maxItems" not in obj:
            missing.append(path)
        for k, v in obj.items():
            missing.extend(check_arrays(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            missing.extend(check_arrays(v, f"{path}[{i}]"))
    return missing

missing_max = check_arrays(schema)
print("Arrays missing maxItems:")
for m in missing_max:
    print(f" - {m}")

with open("scratch/schema_dump_real.json", "w") as f:
    json.dump(schema, f, indent=2)
