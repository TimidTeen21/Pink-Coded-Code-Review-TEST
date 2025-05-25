import sqlite3
import json

# No connection pooling
def get_db():
    return sqlite3.connect(":memory:")

# SQL injection via string formatting
def search_users(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'")
    return cursor.fetchall()

# No input sanitization
def insert_user(data):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (data["name"], data["email"])  # No validation
    )
    db.commit()

# Dumps sensitive data to JSON unsafely
def export_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    return json.dumps(cursor.fetchall())  # No PII masking