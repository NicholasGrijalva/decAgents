import subprocess

def setup():
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        print("Setup complete!")
    except subprocess.CalledProcessError:
        print("Error installing requirements")

if __name__ == "__main__":
    setup()