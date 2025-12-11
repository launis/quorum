import json
from typing import Optional, Type, Any
from pydantic import BaseModel, Field, create_model, ConfigDict
from backend.models.domain import XAIReport
from backend.config import SEED_DATA_PATH

# Mocking the method from XAIReporterAgent
def get_dynamic_schema() -> Optional[Type[BaseModel]]:
    try:
        with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        output_config = next((c for c in data.get('components', []) if c['id'] == 'STANDARD_REPORT_OUTPUT'), None)
        
        if output_config:
            fields = {}
            for field_name in output_config.get('content', []):
                safe_name = field_name.replace('.', '_')
                fields[safe_name] = (Optional[str], Field(default=None, description=f"Dynamic field: {field_name}"))
            
            DynamicReport = create_model(
                'DynamicXAIReport',
                __base__=XAIReport,
                **fields
            )
            return DynamicReport
    except Exception as e:
        print(f"Error: {e}")
        return XAIReport
    return XAIReport

if __name__ == "__main__":
    schema = get_dynamic_schema()
    print("Schema generated successfully.")
    print(json.dumps(schema.model_json_schema(), indent=2))
