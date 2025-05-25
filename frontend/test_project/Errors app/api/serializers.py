import pickle
import yaml

# Dangerous deserialization
def load_pickle(data):
    return pickle.loads(data)  # RCE risk!

# Insecure YAML loading
def load_yaml(data):
    return yaml.unsafe_load(data)  # Code execution!

# Logs sensitive data
def log_user(user):
    print(f"[LOG] User logged in: {user}")  # stdout + no sanitization

# Exposes internal errors to users
def get_user_profile(user_id):
    try:
        # ... fetch user
        return user
    except Exception as e:
        return {"error": str(e)}  # Leaks stack traces