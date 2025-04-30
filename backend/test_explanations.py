# backend/test_explanations.py
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.services.explanation_templates import ExplanationTemplates

print(ExplanationTemplates().get_template('E501'))