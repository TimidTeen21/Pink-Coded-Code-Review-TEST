# backend/app/dependencies.py
from app.services.profile_service import ProfileService
from app.services.explanation_engine import ExplanationEngine

def get_profile_service():
    return ProfileService()

def get_explanation_engine():
    return ExplanationEngine(get_profile_service())