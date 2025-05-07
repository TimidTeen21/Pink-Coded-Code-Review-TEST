from app.routers.analysis import parse_radon_output
from pathlib import Path
import json

def test_parse_radon_output():
    sample_output = json.dumps({
        "file.py": [{
            "type": "function",
            "name": "foo",
            "lineno": 1,
            "complexity": 5,
            "rank": "B"  # Required field
        }]
    })
    
    result = parse_radon_output(sample_output, Path("/fake/path"))
    assert len(result) == 1
    assert result[0]["code"] == "RADON-B"
    assert result[0]["complexity"] == 5