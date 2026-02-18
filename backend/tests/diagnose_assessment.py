
import json
from pydantic import ValidationError
try:
    from backend.api.transformers.assessment import AssessmentTransformer
    print("AssessmentTransformer OK")
except ValidationError as e:
    print("VALIDATION ERROR:")
    print(json.dumps(e.errors(), indent=2, default=str))
except Exception as e:
    if hasattr(e, "errors"):
         print("VALIDATION ERROR (Generic Catch):")
         print(json.dumps(e.errors(), indent=2, default=str))
    else:
        print(f"IMPORT ERROR: {e}")
