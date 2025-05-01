# Test vulnerabilities
password = "admin123"  # B105
pickle.loads(b"data")  # B301
subprocess.call("ls", shell=True)  # B602