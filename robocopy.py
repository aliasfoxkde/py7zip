import subprocess

def copy(src,dst,options=''):
    command = f'robocopy "{src}" "{dst}" /E {options}'
    result = subprocess.run(command,capture_output=True,text=True)
    print(result.stdout)
    if result.returncode==1:
        print(f"Copied files from {src} to {dst}")
