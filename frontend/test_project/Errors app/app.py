import os
import pickle
import subprocess
from flask import Flask, request, render_template_string
from config import SECRET_KEY, DB_PASSWORD
from utils import log_message

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Hardcoded credentials (Security vulnerability)
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# SQL query construction (SQL injection vulnerability)
def get_user(username):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# XSS vulnerable endpoint
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    return render_template_string(f"<h1>Hello {name}!</h1>")

# Command injection vulnerability
@app.route('/ping')
def ping():
    host = request.args.get('host', '127.0.0.1')
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output

# Insecure deserialization
@app.route('/unpickle')
def unpickle():
    data = request.args.get('data')
    obj = pickle.loads(data.encode('latin1'))
    return str(obj)

# Hardcoded sensitive data
@app.route('/dbinfo')
def dbinfo():
    return f"Database password: {DB_PASSWORD}"

# Missing authentication/authorization
@app.route('/admin')
def admin_panel():
    return "Welcome to admin panel"

# Insecure file handling
@app.route('/readfile')
def read_file():
    filename = request.args.get('file')
    with open(filename, 'r') as f:
        return f.read()

# Poor error handling
@app.route('/divide')
def divide():
    a = int(request.args.get('a', 1))
    b = int(request.args.get('b', 1))
    return str(a / b)

# Insecure logging
@app.route('/log')
def log():
    message = request.args.get('message')
    log_message(f"User message: {message}")
    return "Logged"

if __name__ == '__main__':
    app.run(debug=True)