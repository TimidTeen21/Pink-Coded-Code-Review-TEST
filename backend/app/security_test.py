# backend/app/security_test.py
"""
This file contains intentional security vulnerabilities for testing purposes.
"""

import pickle
import subprocess
from flask import Flask
import hashlib  # deprecated and insecure

app = Flask(__name__)
app.debug = True  # Insecure!

def insecure_deserialization():
    data = b"cos\nsystem\n(S'echo hello world'\ntR."
    return pickle.loads(data)  # B301

def shell_injection():
    user_input = "test; rm -rf /"
    subprocess.call(f"echo {user_input}", shell=True)  # B602

def weak_hashing():
    return hashlib.md5("password".encode()).hexdigest()  # B303