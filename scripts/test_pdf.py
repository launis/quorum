import sys
import asyncio
from backend.services.pdf_generator import PdfReportService

# Mock repository to avoid DB connection issues in simple script
class MockRepo:
    async def get_execution(self, exec_id):
        return None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pdf.py <execution_id>")
        sys.exit(1)
        
    execution_id = sys.argv[1]
    repo = MockRepo()
    svc = PdfReportService(repository=repo)
    print(f"Generating PDF for {execution_id}...")
    
    # We don't have the original execution_trace easily in this mock script
    # Let's just use the CLI or a full integration test instead of manual script.
    pass

if __name__ == "__main__":
    asyncio.run(main())
