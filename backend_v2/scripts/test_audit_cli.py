import asyncio
import os
import sys
import traceback

# Provide path to backend rules
sys.path.insert(0, r"c:\src\quorum")

try:
    import PyPDF2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def get_pdf_text(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

async def main():
    import logging

    from backend_v2.logging_config import setup_logging
    setup_logging(log_level=logging.INFO)

    test_dir = r"c:\src\quorum\data\files\548d78cd-d540-44a3-bc3e-965064803a40"
    chat_log = get_pdf_text(os.path.join(test_dir, "keskusteluhistoria SITRA.pdf"))
    product = get_pdf_text(os.path.join(test_dir, "lopputuote sitra.pdf"))
    reflection = get_pdf_text(os.path.join(test_dir, "Reflektiodokumentti sitra.pdf"))

    print(f"Extracted Character Lengths:\n - Chat: {len(chat_log)}\n - Product: {len(product)}\n - Reflection: {len(reflection)}")

    from fastapi import BackgroundTasks

    # Initialize Task Registry / Hook Registry
    from backend_v2.api.dependencies import TokenData
    from backend_v2.database.factory import get_repository
    from backend_v2.models.v2_core import ExecutionCreate, WorkflowInputs
    from backend_v2.services.execution import ExecutionService
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
    from backend_v2.settings import get_settings

    from backend_v2.models.auth import UserRole
    user = TokenData(
        id="10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b", # Match system root ID from DB
        email="system@local",
        role=UserRole.ROOT,
        organization_id="436d84de-c526-43b7-93ef-634912be0d2f"
    )

    settings = get_settings()
    repo = await get_repository(settings)
    compiler = PromptCompiler()
    executor = DAGExecutor(repo, compiler)
    service = ExecutionService(repo=repo, executor=executor)

    payload = ExecutionCreate(
        workflow_id="workflow_courtroom_20_full_audit",
        raw_inputs=WorkflowInputs(**{
            "chat_log": chat_log,
            "product_text": product,
            "reflection_text": reflection
        })
    )

    bt = BackgroundTasks()

    print("\n--- Starting Execution ---")
    try:
        record = await service.start_execution(user, payload, bt)
        print(f"Background Process Triggered. Execution ID: {record.id}")

        print("\n--- Awaiting Background GraphEngine Completeness ---")
        for task in bt.tasks:
            # We explicitly await the async background function so we can capture exactly
            # when it's done for the test output
            await task.func(*task.args, **task.kwargs)

        final_record = await service.get_execution(user, record.id)
        print("\n--- Final Status ---")
        print(final_record.status)

        if final_record.error:
            print(f"ERROR: {final_record.error}")

        print("\n--- Node Results Extracted ---")
        for k, v in final_record.results.items():
            print(f"Node '{k}': {len(str(v))} chars")

        print("\n--- Odotetaan Logfire-datan siirtymistä EU-pilveen (5 sekuntia) ---")
        await asyncio.sleep(5)

    except Exception:
        print("\n--- FAST-FAIL TRACE ---")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
