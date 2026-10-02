import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

os.chdir(SRC)
subprocess.run([sys.executable, "main.py"], check=False)
