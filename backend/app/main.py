# backend/app/main.py
from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, profile_router, analysis, files, feedback_router
from app.routers.explanation_router import router as explanation_router
import asyncio

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Pink Coded",
    description="AI-Powered Code Review Tool",
        version="0.1.0",
        redirect_slashes=False
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # For development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers with proper prefixes
# Ensure this comes after CORS middleware
app.include_router(auth.router)
app.include_router(files.router, prefix="/api/v1")
app.include_router(analysis.router)
app.include_router(explanation_router, prefix="/api/v1")
app.include_router(feedback_router.router, prefix="/api/v1")
app.include_router(profile_router.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await asyncio.wait_for(analysis.cleanup_temp_dirs(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.error("Timeout during cleanup")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)