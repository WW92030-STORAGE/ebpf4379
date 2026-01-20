import subprocess

def exec_(cmd):
    subprocess.run(cmd, shell = True)