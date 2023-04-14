import sys
import subprocess

# implement pip as a subprocess:
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
subprocess.check_call([sys.executable, 'pip', 'install', '--upgrade', 'setuptools'])