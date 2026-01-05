from contextvars import ContextVar

# Global context variable for Execution ID
execution_id_var: ContextVar[str | None] = ContextVar("execution_id", default=None)


def set_execution_context(execution_id: str):
    execution_id_var.set(execution_id)


def get_execution_context() -> str | None:
    return execution_id_var.get()


def clear_execution_context():
    execution_id_var.set(None)
