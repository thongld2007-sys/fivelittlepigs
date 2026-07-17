import uvicorn
import webbrowser
import threading
import time
from backend.config import Config
from backend.database import init_db

def open_browser():
    # Wait 2 seconds for server to bind
    time.sleep(2)
    url = f"http://127.0.0.1:{Config.PORT}"
    print(f"[*] Opening browser automatically to: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("[*] Initializing local database...")
    init_db()
    
    # Start browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start uvicorn server
    print(f"[*] Starting local server on host {Config.HOST} port {Config.PORT}...")
    uvicorn.run("backend.app:app", host=Config.HOST, port=Config.PORT, reload=False)
