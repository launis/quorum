import asyncio
import os
import logging
from backend_v2.database.factory import get_repository
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.blueprint import BlueprintTransformer

from backend_v2.settings import get_settings

logging.basicConfig(level=logging.INFO)

async def test_pdf():
    repo = await get_repository(get_settings())
    executions = await repo.get_all_executions()
    if not executions:
        print("No executions")
        return
    
    # Get latest
    exe = executions[0] # assuming get_all_executions sorts or we can just pick the first
    print(f"Testing PDF for {exe.id}")
    
    # Build rendering payload
    transformer = BlueprintTransformer(repo)
    payload = await transformer.build_render_payload(exe.id, "fi")
    
    pdf_service = PdfReportService(repo)
    pdf_bytes = await pdf_service.generate_execution_pdf(exe.id, payload)
    
    # We can fetch the raw HTML by bypassing generate_execution_pdf and calling the jinja template directly
    template = pdf_service.env.get_template("report_template.jinja2")
    html_out = template.render(
        execution_id=exe.id,
        workflow_name="Test WF",
        frozen_context=exe.frozen_context.model_dump() if exe.frozen_context else {},
        results=exe.results or {},
        rendered_blueprint=payload,
        printed_at="2026-03-18"
    )
    with open("c:/src/quorum/test_report.html", "w", encoding="utf-8") as f:
        f.write(html_out)
    
    out_path = os.path.abspath("test_report.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
        
    print(f"PDF generated to {out_path}")

if __name__ == "__main__":
    asyncio.run(test_pdf())
