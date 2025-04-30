# Should trigger B105 (hardcoded password) and B602 (subprocess call)
password = "secret123"
import subprocess
subprocess.call(["ls", "-la"])