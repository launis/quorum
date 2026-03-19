import json
from tinydb import TinyDB, Query
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

def show_schema():
    db = TinyDB('data/db_v2.json')
    table = db.table('prompt_blocks')
    # Use blk_1e33ce78623943af9d5ce39ce6620478 (Falsification Audit) as an example
    raw_block = table.get(Query().id == 'blk_1e33ce78623943af9d5ce39ce6620478')
    if not raw_block:
        # Just grab the first matrix block we can find
        for b in table.all():
            if b.get('scales') and len(b['scales']) > 0:
                raw_block = b
                break

    if not raw_block:
        print("No matrix blocks found.")
        return

    pb = PromptBlock.model_validate(raw_block)
    compiler = PromptCompiler()
    
    # We pass criteria as a list of dicts. 
    # The compiler expects a dictionary representation of the criteria.
    # In the actual pipeline, the block itself is treated as a criterion since V2 PromptBlock IS the criteria.
    criteria = [raw_block]
    
    SchemaClass = compiler.build_dynamic_schema("TestSchema", criteria, require_justification=True)
    
    print("\n" + "="*80)
    print(f"Opaque ID (Schema Type): {pb.id}")
    print("="*80)
    
    schema_json = SchemaClass.model_json_schema()
    
    # Print the specific field's description
    prop = schema_json['properties'][pb.id]
    
    print("\nTÄMÄ ON SE TARKKA TEKSTI, JOKA LÄHTEE LLM:lle (Vertex AI Structured Output 'description' kenttänä):\n")
    print("-" * 80)
    print(prop.get('description', ''))
    print("-" * 80)

if __name__ == "__main__":
    show_schema()
