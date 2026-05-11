import os
import re

# 1. Update backend_v2/services/orchestrator/strategies/base.py
base_path = "backend_v2/services/orchestrator/strategies/base.py"
with open(base_path, "r", encoding="utf-8") as f:
    base_code = f.read()

if "arq_pool: Any | None = None" not in base_code:
    base_code = base_code.replace(
        "    def __init__(",
        "    def __init__("
    ).replace(
        "        prompt_compiler: Any,\n    ):",
        "        prompt_compiler: Any,\n        arq_pool: Any | None = None,\n    ):"
    ).replace(
        "        self.compiler = prompt_compiler",
        "        self.compiler = prompt_compiler\n        self.arq_pool = arq_pool"
    )
    with open(base_path, "w", encoding="utf-8") as f:
        f.write(base_code)


# 2. Update backend_v2/services/orchestrator/dag_executor.py
dag_path = "backend_v2/services/orchestrator/dag_executor.py"
with open(dag_path, "r", encoding="utf-8") as f:
    dag_code = f.read()

if "arq_pool: Any | None = None" not in dag_code:
    dag_code = dag_code.replace(
        "        scoring_strategy: ScoringStrategy = ScoringStrategy.WATERFALL,\n    ) -> ExecutionRecord:",
        "        scoring_strategy: ScoringStrategy = ScoringStrategy.WATERFALL,\n        arq_pool: Any | None = None,\n    ) -> ExecutionRecord:"
    )
    
    # Pass arq_pool to _execute_node
    dag_code = dag_code.replace(
        "                emitted_events = await self._execute_node(\n                    step=step,",
        "                emitted_events = await self._execute_node(\n                    arq_pool=arq_pool,\n                    step=step,"
    )
    
    # Update _execute_node signature
    dag_code = dag_code.replace(
        "    async def _execute_node(\n        self,",
        "    async def _execute_node(\n        self,\n        arq_pool: Any | None,"
    )
    
    # Pass arq_pool to LLMNodeStrategy
    dag_code = dag_code.replace(
        "                    self.compiler,\n                )",
        "                    self.compiler,\n                    arq_pool=arq_pool,\n                )"
    )
    with open(dag_path, "w", encoding="utf-8") as f:
        f.write(dag_code)


# 3. Update backend_v2/worker.py execute_workflow_job to pass arq_pool
worker_path = "backend_v2/worker.py"
with open(worker_path, "r", encoding="utf-8") as f:
    worker_code = f.read()

if "arq_pool=redis" not in worker_code:
    worker_code = worker_code.replace(
        "            updated_exec_record = await engine.execute_workflow(\n                execution_id=exec_id,\n                workflow=workflow_def,\n                raw_inputs=inputs_obj,\n                strictness_level=strictness_level,\n            )",
        "            redis = ctx.get(\"redis\")\n            updated_exec_record = await engine.execute_workflow(\n                execution_id=exec_id,\n                workflow=workflow_def,\n                raw_inputs=inputs_obj,\n                strictness_level=strictness_level,\n                arq_pool=redis,\n            )"
    )
    with open(worker_path, "w", encoding="utf-8") as f:
        f.write(worker_code)

print("Architecture prepared for Arq MAP-REDUCE")
