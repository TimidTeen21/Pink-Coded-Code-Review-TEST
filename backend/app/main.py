from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis, files 


app = FastAPI(
    title="Pink Coded",
    description="AI-Powered Code Review Tool",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # For development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import analysis, files
app.include_router(files.router) 
app.include_router(analysis.router)