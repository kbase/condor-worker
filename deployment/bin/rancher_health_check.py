#!/miniconda/bin/python3
import subprocess
import sys
cmd = "condor_status $(hostname) -af NODE_IS_HEALTHY"
result = subprocess.check_output(cmd,shell=True).decode().strip()
if result == "true":
  sys.exit(0)
else:
  sys.exit(1)
