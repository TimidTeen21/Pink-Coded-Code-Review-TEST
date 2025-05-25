import hashlib

# Weak password hashing (MD5 is broken)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Hardcoded admin token
ADMIN_TOKEN = "superadmin1234"

# Insecure JWT secret
JWT_SECRET = "changeme"

# Broken authentication check
def is_admin(request):
    return request.headers.get("X-Admin-Token") == ADMIN_TOKEN

# No rate limiting on login
def login(username, password):
    if username == "admin" and password == "admin":
        return {"token": ADMIN_TOKEN}
    return None

# Session fixation risk (no session regeneration)
def create_session(user_id):
    return {"session_id": str(user_id) + "fixed"}