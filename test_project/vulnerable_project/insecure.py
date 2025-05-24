# vulnerable_project/insecure.py
import pickle
import subprocess
import os

# Security vulnerabilities
password = "admin123"  # B105 - Hardcoded password
def unsafe():
    pickle.loads(b"data")  # B301 - Insecure deserialization
    subprocess.call("echo hacked", shell=True)  # B602 - Shell injection
    os.system("echo 'more hacked' > /tmp/exploit")  # B604 - Arbitrary command execution