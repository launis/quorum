import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.models.v2_core import ExecutionRecord, Workflow, FrozenContext, ExecutionStatus
from backend_v2.services.pdf_generator import PdfReportService
from tinydb import TinyDB, Query

LOCAL_DB_PATH = os.path.join(PROJECT_ROOT, "data", "db_v2.json")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "test_grid_report.pdf")

class MockRepo:
    def __init__(self, execution: ExecutionRecord, workflow_dict: dict):
        self._exec = execution
        self._wf_dict = workflow_dict
        
    async def get_execution(self, exec_id: str):
        return self._exec
        
    async def get_workflow_by_id(self, wf_id: str):
        return self._wf_dict

async def test_pdf_grid():
    db = TinyDB(LOCAL_DB_PATH, encoding="utf-8")
    workflows_table = db.table("workflows")
    
    # 1. Fetch the workflow we modified
    wf_data = workflows_table.get(Query().id == "workflow_courtroom_20_full_audit")
    if not wf_data:
        print("ERROR: Workflow not found in local db.")
        return
        
    workflow = Workflow.model_validate(wf_data)
    
    # 2. Mock an ExecutionRecord
    mock_results = {
        "step_logician": {
            "matrix_toulmin": {"x_value": 4.0, "y_value": 3.0, "x_note_text": "Toulmin X Note", "y_note_text": "Toulmin Y Note"},
            "matrix_bloom": {"x_value": 2.5, "y_value": 4.5}
        },
        "step_xai_reporter": {
            "matrix_xai_reporter": {"x_value": 1.0, "y_value": 2.0},
            "matrix_taskxai_clarity": {"x_value": 3.0, "y_value": 4.0}
        },
        "step_judge": {
            "matrix_judge_normalized": {"x_value": 5.0, "y_value": 5.0} # Used as Z for 3d_scatter
        },
        "step_profiler": {
            "matrix_kahneman_normalized": 7.5
        }
    }
    
    frozen_ctx = FrozenContext(
        ui_hints_snapshot={}
    )
    
    execution = ExecutionRecord(
        id="test_exec_123",
        workflow_id=workflow.id,
        status=ExecutionStatus.COMPLETED,
        results=mock_results,
        raw_inputs={"chat_log": {"conversation": []}},
        frozen_context=frozen_ctx
    )
    
    repo = MockRepo(execution, wf_data)
    generator = PdfReportService(repository=repo)
    
    # 3. Generate PDF
    try:
        # Pass the pre-assembled blueprint dictionary like the worker does
        blueprint_payload = None
        if workflow.render_blueprints and "default" in workflow.render_blueprints:
            blueprint_payload = workflow.render_blueprints["default"].model_dump()
            
        pdf_bytes = await generator.generate_execution_pdf(execution.id, blueprint_payload)
        
        with open(OUTPUT_PDF, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"SUCCESS: PDF generated and saved to {OUTPUT_PDF}")
        print(f"File size: {os.path.getsize(OUTPUT_PDF)} bytes")
    except Exception as e:
        print(f"FAILED to generate PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_grid())
