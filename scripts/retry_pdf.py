import asyncio

from backend_v2.worker import generate_pdf_task


async def main() -> None:
    print("Generating PDF...")
    await generate_pdf_task("exe_68236bce05da444fabbcf6bbc4b2291a", "fi", "prf_5d6e7f8091a2b3c4")
    print("Done generating PDF.")


if __name__ == "__main__":
    asyncio.run(main())
