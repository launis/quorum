from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Initialize App
app = FastAPI(
    title="Cognitive Quorum API",
    description="REST API for the Cognitive Quorum Multi-Agent System",
    version="2.0.0"
)

# CORS Configuration
# Allow all origins for development convenience (Streamlit runs on different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler for Debugging
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    print(f"Global Error: {error_msg}")
    with open("backend_error.log", "a") as f:
        f.write(f"--- Error at {request.url} ---\n")
        f.write(error_msg + "\n")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

from src.database.initialization import initialize_database

@app.on_event("startup")
async def startup_event():
    print("Executing startup tasks...")
    initialize_database()

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Cognitive Quorum API",
        "version": "2.0.0"
    }

# Import and Include Routers
from src.api.routers import db_router, llm_router, orchestrator_router, tools_router
app.include_router(db_router.router, prefix="/db", tags=["Database"])
app.include_router(llm_router.router, prefix="/llm", tags=["LLM"])
app.include_router(orchestrator_router.router, prefix="/orchestrator", tags=["Orchestrator"])
app.include_router(tools_router.router, prefix="/tools", tags=["Tools"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
