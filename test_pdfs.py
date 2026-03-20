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
    
    # Target directory
    out_dir = Path("docs/pdf_tests")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    variants = ["default", "1d_metrics", "2d_compare", "3d_complex"]
    
    for variant in variants:
        print(f"Generating PDF for variant '{variant}'...")
        try:
            # Generate the specific blueprint variant payload
            payload = await transformer.build_render_payload(exec_id, accept_language="fi", variant=variant)
            
            # Render PDF with the Jinja2 template and Weasyprint
            pdf_bytes = await pdf_service.generate_execution_pdf(exec_id, blueprint_payload=payload)
            
            # Save the file
            out_path = out_dir / f"test_render_fi_{variant}_v5.pdf"
            with open(out_path, "wb") as f:
                f.write(pdf_bytes)
            print(f" -> Saved {out_path} ({len(pdf_bytes)} bytes)")
        except Exception as e:
            print(f" -> FAILED to generate '{variant}': {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
