import subprocess

def exec_(cmd):
    return subprocess.run(cmd, shell = True,     
    capture_output=True,
    text=True,
    check=True # Optional: raise an exception if the command fails
    ).stdout