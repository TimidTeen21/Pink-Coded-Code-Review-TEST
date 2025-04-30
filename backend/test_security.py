# INSECURE CODE - FOR TESTING ONLY
import pickle
import subprocess

def insecure_deserialization():
    data = b"cos\nsystem\n(S'echo hacked'\ntR."  # Arbitrary code execution
    pickle.loads(data)  # B301

def shell_injection():
    user_input = "test; rm -rf /"
    subprocess.call(f"echo {user_input}", shell=True)  # B602