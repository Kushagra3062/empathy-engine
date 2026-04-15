import subprocess
import sys
import os

# Add the 'backend' folder to the Python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def start_server():
    print("🚀 Starting Empathy Engine Backend...")
    try:
        import uvicorn
        # Run uvicorn from the root, pointing to app.main:app
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=os.path.join(os.getcwd(), 'backend'))
    except ImportError:
        print("❌ Uvicorn not found. Please run 'pip install -r backend/requirements.txt'")

if __name__ == "__main__":
    start_server()
