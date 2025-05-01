import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.models import UserProfile

print("UserProfile class:", UserProfile)
print("Sample profile:", UserProfile(user_id="test123"))