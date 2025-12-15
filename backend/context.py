from contextvars import ContextVar
from typing import Optional

# Global context variable for Execution ID
execution_id_var: ContextVar[Optional[str]] = ContextVar("execution_id", default=None)

def set_execution_context(execution_id: str):
    execution_id_var.set(execution_id)

def get_execution_context() -> Optional[str]:
    return execution_id_var.get()

def clear_execution_context():
    execution_id_var.set(None)
