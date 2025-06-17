import sys
import subprocess


def run_command(command, check=True):
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}: {e}")
        sys.exit(e.returncode)
