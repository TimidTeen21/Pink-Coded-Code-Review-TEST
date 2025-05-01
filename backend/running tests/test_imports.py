from app.models import Issue
from app.services.explanation_engine import ExplanationEngine
from app.services.profile_service import ProfileService

def test_initialization():
    service = ProfileService()
    engine = ExplanationEngine(service)
    print("All imports and initialization working!")

if __name__ == "__main__":
    test_initialization()