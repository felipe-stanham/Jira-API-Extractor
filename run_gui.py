#!/usr/bin/env python3
"""
Streamlit GUI Runner for Jira API Extractor

This script runs the Streamlit GUI and automatically opens the browser.
"""

import subprocess
import sys
import webbrowser
import time
import threading
import socket
import os
from dotenv import load_dotenv

def is_port_open(port):
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def open_browser_when_ready(url, port, max_wait=10):
    """Open browser when the Streamlit server is ready."""
    # Port is now passed as parameter
    
    # Wait for server to be ready
    for _ in range(max_wait * 2):  # Check every 0.5 seconds
        if is_port_open(port):
            time.sleep(1)  # Give it a moment to fully load
            webbrowser.open(url)
            print(f"🌐 Opened browser at {url}")
            break
        time.sleep(0.5)

def main():
    """Run the Streamlit app with automatic browser opening."""
    print("🚀 Starting Jira Data Extractor GUI...")
    print("📊 Streamlit interface will open in your default browser")
    
    # Load environment variables
    load_dotenv()
    
    # Get port from .env file or use default
    port = int(os.getenv('STREAMLIT_PORT', '8501'))
    
    # URL where Streamlit will run
    url = f"http://localhost:{port}"
    
    print(f"🌐 Starting on port {port}")
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(
        target=open_browser_when_ready, 
        args=(url, port)
    )
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()
