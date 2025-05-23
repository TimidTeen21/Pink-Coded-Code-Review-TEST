# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\__init__.py
from fastapi import FastAPI
from .routers import analysis, files, auth, profile_router

def create_app() -> FastAPI:
    """Application factory pattern"""
    app = FastAPI()
    return app

app = create_app()

def configure_routers():
    """Configure all routers"""
    app.include_router(auth.router)
    app.include_router(profile_router.router)
    app.include_router(files.router)
    app.include_router(analysis.router)

configure_routers()