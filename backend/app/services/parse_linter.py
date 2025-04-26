from typing import List, Dict, Any
import json

def parse_linter_output(output: str, linter: str) -> List[Dict[str, Any]]:
    try:
        if not output.strip():
            return []
            
        if linter == "ruff":
            issues = json.loads(output)
            return [{
                "type": "error" if issue["code"].startswith("E") else "warning",
                "file": issue["filename"],
                "line": issue["location"]["row"],
                "message": issue["message"],
                "code": issue["code"]
            } for issue in issues]
            
        elif linter == "pylint":
            issues = json.loads(output)
            return [{
                "type": issue["type"].lower(),
                "file": issue["path"],
                "line": issue["line"],
                "message": issue["message"],
                "code": issue["symbol"]
            } for issue in issues]
            
    except Exception as e:
        print(f"Parse error: {str(e)}")
        return []

def parse_ruff_output(output: str) -> list:
    try:
        import json
        issues = json.loads(output)
        return [{
            "type": "error" if issue['severity'] == 'error' else "warning",
            "file": issue['location']['file'],
            "line": issue['location']['row'],
            "message": issue['message'],
            "code": issue['code']
        } for issue in issues]
    except:
        return []

def parse_pylint_output(output: str) -> list:
    try:
        import json
        issues = json.loads(output)
        return [{
            "type": "error" if issue['type'] == 'error' else "warning",
            "file": issue['path'],
            "line": issue['line'],
            "message": issue['message'],
            "code": issue['message-id']
        } for issue in issues]
    except:
        return []