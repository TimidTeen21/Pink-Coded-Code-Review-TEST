# backend/test_integration.py
import sys
from pathlib import Path
import os
import shutil

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.models import Issue
    from app.services import ExplanationEngine, ProfileService
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install httpx pytest")
    sys.exit(1)

def setup_test_environment():
    """Prepare clean test environment"""
    profile_dir = Path("user_profiles")
    if profile_dir.exists():
        shutil.rmtree(profile_dir)
    profile_dir.mkdir(exist_ok=True)

def test_full_workflow():
    """Test complete flow from analysis to feedback"""
    setup_test_environment()
    client = TestClient(app)
    
    # Test data
    test_user = "test_user_integration"
    test_issue = Issue(
        code="E501",
        message="Line too long",
        file="test.py",
        line=10
    )
    
    try:
        # 1. Test service layer
        profile_service = ProfileService()
        engine = ExplanationEngine(profile_service)
        explanation = engine.explain(test_issue, test_user)
        assert "PEP 8" in explanation['description'], "Service layer failed"
        
        # 2. Test API endpoints
        # Template endpoint
        template_response = client.get(
            f"/api/v1/explanations/template/{test_issue.code}",
            params={"level": "intermediate"}
        )
        assert template_response.status_code == 200, "Template endpoint failed"
        
        # Feedback endpoint
        feedback_response = client.post(
            "/api/v1/feedback/explanation",
            json={
                "user_id": test_user,
                "issue_code": test_issue.code,
                "was_helpful": True
            }
        )
        assert feedback_response.status_code == 200, "Feedback endpoint failed"
        
        # 3. Verify persistence
        profile = profile_service.get_profile(test_user)
        assert test_issue.code in profile.seen_issues, "Persistence failed"
        
        print("✅ All integration tests passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_full_workflow():
        sys.exit(0)
    else:
        sys.exit(1)