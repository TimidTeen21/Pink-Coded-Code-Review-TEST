# backend/test_explanation_engine.py
from app.models import Issue, UserProfile
from app.services.explanation_engine import ExplanationEngine
from app.services.profile_service import ProfileService
import os

def test_explanation_engine():
    # Setup
    profile_service = ProfileService()
    engine = ExplanationEngine(profile_service)
    test_user = "test_user_123"
    
    # Create test issue
    test_issue = Issue(
        code="E501",
        message="Line too long (120 > 79 characters)",
        file="test.py",
        line=10,
        severity="warning"
    )
    
    # Test 1: Verify basic template
    explanation = engine.explain(test_issue, test_user)
    assert "PEP 8" in explanation['why'], "PEP 8 reference missing"
    assert "10" in explanation['description'], "Line number not in description"
    
    # Test 2: Verify beginner level
    profile = profile_service.get_profile(test_user)
    profile.experience_level = "beginner"
    profile_service.save_profile(profile)
    beginner_explanation = engine.explain(test_issue, test_user)
    assert "hard to read" in beginner_explanation['why'], "Beginner explanation mismatch"
    
    # Test 3: Verify OOP integration
    profile.known_concepts.add("OOP")
    profile_service.save_profile(profile)
    oop_explanation = engine.explain(test_issue, test_user)
    assert "refactoring" in oop_explanation['fix'].lower(), "OOP advice missing"
    
    print("✅ All explanation engine tests passed!")

if __name__ == "__main__":
    # Ensure templates file exists
    if not os.path.exists("app/services/explanation_templates.json"):
        print("Error: Missing explanation_templates.json")
    else:
        test_explanation_engine()