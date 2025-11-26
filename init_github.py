"""
Initialize Git repository and create GitHub repo
Run this after setting up the project
"""
import subprocess
import sys

def init_git():
    print("Initializing Git repository...")
    
    commands = [
        ['git', 'init'],
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Initial commit: KyleH System Monitor'],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  OK: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: {' '.join(cmd)}")
            print(f"    {e.stderr}")
            return False
    
    print("\nGit repository initialized!")
    print("\nTo push to GitHub:")
    print("  1. Create repo on GitHub: https://github.com/new")
    print("  2. Name it: kyleh")
    print("  3. Run these commands:")
    print("     git remote add origin https://github.com/YOUR_USERNAME/kyleh.git")
    print("     git branch -M main")
    print("     git push -u origin main")
    
    return True

if __name__ == "__main__":
    init_git()
