from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis, files
from app.routers import feedback_router
from .routers import feedback_router
from app.routers.explanation_router import router as explanation_router
from fastapi import FastAPI


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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(files.router) 
app.include_router(analysis.router)
app.include_router(explanation_router)
app.include_router(feedback_router.router, prefix="/api/v1")