import asyncio

from backend_v2.worker import generate_pdf_task


async def main() -> None:
    print("Generating PDF...")
    await generate_pdf_task("exe_cd1e2cae3bb7497992b72d401d0ff2d2", "fi", "prf_5d6e7f8091a2b3c4")
    print("Done generating PDF.")


if __name__ == "__main__":
    asyncio.run(main())
