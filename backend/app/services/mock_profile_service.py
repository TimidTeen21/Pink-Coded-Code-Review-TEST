# backend/app/services/mock_profile_service.py
from app.models import UserProfile

class MockProfileService:
    def get_profile(self, user_id):
        return UserProfile(
            user_id=user_id,
            experience_level="intermediate",
            seen_issues={},
            known_concepts=[]
        )
    
    def log_explanation_usage(self, user_id, issue_code):
        print(f"Mock: Logged usage of {issue_code} by user {user_id}")
    
    def save_profile(self, profile):
        print(f"Mock: Saved profile for {profile.user_id}")