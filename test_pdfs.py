import asyncio
import os
from pathlib import Path
from backend_v2.settings import get_settings
from backend_v2.database.factory import get_repository
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.blueprint import BlueprintTransformer

async def main():
    exec_id = "exe_f5de7581c7f04f18838ee8f875211bde"
    settings = get_settings()
    repo = await get_repository(settings)
    
    pdf_service = PdfReportService(repo)
    transformer = BlueprintTransformer(repo)
    
    out_dir = Path("docs/pdf_tests")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating Fast-Fail MVC PDF for Execution '{exec_id}'...")
    try:
        # Generate the strict DTO instead of the legacy dynamic blueprint
        payload = await transformer.build_report_dto(exec_id, accept_language="fi")
        
        # Render PDF with the Jinja2 template and Weasyprint (passing report_dto instead of blueprint_payload)
        pdf_bytes = await pdf_service.generate_execution_pdf(exec_id, report_dto=payload)
        
        # Save the file
        out_path = out_dir / f"test_render_fi_mvc_dto.pdf"
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)
        print(f" -> SUCCESS! Saved {out_path} ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f" -> FAILED to generate DTO-based PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
