# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\models\user_profile.py
from pydantic import BaseModel

class UserProfile(BaseModel):
    user_id: str
    experience_level: str = "intermediate"