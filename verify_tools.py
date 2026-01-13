"""Verify Tools Router Compliance."""

import asyncio
import logging

from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from backend.api.tools_router import router as tools_router
from backend.main import http_exception_handler

logging.basicConfig(level=logging.ERROR)

app = FastAPI()
app.include_router(tools_router)
app.exception_handler(HTTPException)(http_exception_handler)


async def main():
    """Run verification tests."""
    print("Verifying Tools Router Compliance...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test 400 SSRF_PROTECTION_BLOCKED
        print("Test 1: Web Scrape Localhost -> Expect 400 SSRF_PROTECTION_BLOCKED")
        resp = await ac.post("/tools/web-scrape", json={"url": "http://127.0.0.1"})
        data = resp.json()
        print(f"Response: {data}")

        if resp.status_code != 400:
            raise RuntimeError(f"FAILED TC1: Status {resp.status_code} != 400")
        if data.get("error_code") != "SSRF_PROTECTION_BLOCKED":
            raise RuntimeError(f"FAILED TC1: Code {data.get('error_code')} != SSRF_PROTECTION_BLOCKED")

        # Test 400 NO_CONTENT_PROVIDED
        print("Test 2: Extract Text Empty -> Expect 400 NO_CONTENT_PROVIDED")
        resp = await ac.post("/tools/extract-text")
        data = resp.json()
        print(f"Response: {data}")

        if resp.status_code != 400:
            raise RuntimeError(f"FAILED TC2: Status {resp.status_code} != 400")
        if data.get("error_code") != "NO_CONTENT_PROVIDED":
            raise RuntimeError(f"FAILED TC2: Code {data.get('error_code')} != NO_CONTENT_PROVIDED")

    print("TOOLS ROUTER VERIFIED")


if __name__ == "__main__":
    asyncio.run(main())
