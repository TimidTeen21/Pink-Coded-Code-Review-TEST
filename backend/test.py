import sys
from pathlib import Path

# Manually add the app directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.explanation_templates import ExplanationTemplates

print("Testing template loading...")
print(ExplanationTemplates().get_template('E501'))