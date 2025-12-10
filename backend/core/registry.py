from typing import Callable, Any, Type, Optional
from tinydb import TinyDB
from backend.config import DB_PATH
from backend.models import domain as schemas
from backend.services import hooks
from pydantic import BaseModel

class DatabaseClient:
    """
    Wrapper for TinyDB database access.
    """
    def __init__(self):
        self.db = TinyDB(DB_PATH, encoding='utf-8')

    def get_table(self, table_name: str):
        """Returns a TinyDB table."""
        return self.db.table(table_name)

class SchemaRegistry:
    """
    Registry for retrieving Pydantic models/schemas dynamically.
    """
    @staticmethod
    def get_schema(schema_name: str) -> Type[BaseModel]:
        """
        Retrieves a Pydantic model class by name from backend.models.domain.
        """
        try:
            return getattr(schemas, schema_name)
        except AttributeError:
            raise ValueError(f"Schema '{schema_name}' not found in backend.models.domain")

class HookRegistry:
    """
    Registry for retrieving hook functions.
    """
    @staticmethod
    def get_hook(hook_name: str) -> Callable:
        """
        Retrieves a hook function by name.
        """
        # Mapping of hook names to actual functions in backend.services.hooks
        hook_map = {
            "sanitize": hooks.sanitize_and_anonymize_input,
            "rag_retrieval": hooks.execute_rag_retrieval,
            "google_search": hooks.execute_google_search, 
            "detect_performativity": hooks.detect_performative_patterns,
            "calculate_scores": hooks.calculate_final_scores,
            "generate_report": hooks.generate_jinja2_report,
            "parse_analyst": hooks.parse_analyst_output,
            "parse_logician": hooks.parse_logician_output,
            "parse_falsifier": hooks.parse_logical_falsifier_output,
            "parse_overseer": hooks.parse_factual_overseer_output,
            "parse_causal": hooks.parse_causal_analyst_output,
            "parse_detector": hooks.parse_performativity_detector_output,
            "parse_judge": hooks.parse_judge_output,
            "ensure_tainted_data": hooks.ensure_tainted_data_content
        }

        hook_func = hook_map.get(hook_name)
        if not hook_func:
            # Fallback: check if the hook exists directly in backend.services.hooks by name
            if hasattr(hooks, hook_name):
                return getattr(hooks, hook_name)
            raise ValueError(f"Hook '{hook_name}' not found in registry or backend.services.hooks")
        
        return hook_func
