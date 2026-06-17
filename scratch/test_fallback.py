from pydantic import BaseModel

from backend_v2.services.llm_task_executor import _build_null_fallback


class M(BaseModel):
    exact_quotes: list[str] | None = None

m = M(exact_quotes=['abc'])
res = _build_null_fallback(M, m)
print("Result:", res.exact_quotes)
