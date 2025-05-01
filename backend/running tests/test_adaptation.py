# Test script: backend/test_adaptation.py
from app.services.profile_service import ProfileService

def test_learning_progression():
    service = ProfileService()
    user_id = "test_user_123"
    
    # Start as intermediate
    profile = service.get_profile(user_id)
    print(f"Initial level: {profile.experience_level}")  # Should be "intermediate"
    
    # Simulate successful understanding
    for _ in range(3):
        service.update_level_based_on_feedback(
            user_id, was_helpful=True, issue_complexity="intermediate"
        )
    
    profile = service.get_profile(user_id)
    print(f"After 2 failures: {profile.experience_level}")  # Should be "intermediate