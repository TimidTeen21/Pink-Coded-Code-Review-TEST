# backend/test_integration_fixed.py
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    import toml
    from fastapi.testclient import TestClient
    from app.main import app
    from app.models import Issue
    from app.services import ExplanationEngine, ProfileService
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install requirements with:")
    print("pip install -r requirements-test.txt")
    sys.exit(1)

def test_workflow():
    try:
        client = TestClient(app, raise_server_exceptions=False)
        profile_service = ProfileService()
        engine = ExplanationEngine(profile_service)
        
        test_issue = Issue(
            code="E501",
            message="Test message",
            file="test.py",
            line=10
        )
        
        # Service test
        explanation = engine.explain(test_issue, "test_user")
        assert "description" in explanation, "Explanation missing description"
        
        # API test
        response = client.get("/api/v1/explanations/template/E501?level=intermediate")
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        
        print("✅ All integration tests passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    if not test_workflow():
        sys.exit(1)