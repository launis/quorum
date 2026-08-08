import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend_v2.worker import generate_pdf_task


async def main() -> None:
    print("Generating PDF...")
    await generate_pdf_task("exe_99086245d3af448f872c408f9dd7445a", "fi", "prf_5d6e7f8091a2b3c4")
    print("Done generating PDF.")

if __name__ == "__main__":
    asyncio.run(main())
