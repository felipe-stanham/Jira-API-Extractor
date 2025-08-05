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

def get_config_file_path():
    """Get the path for JiraExtractor.env file, handling bundled executables."""
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        if sys.platform == 'darwin' and '.app' in sys.executable:
            # macOS .app bundle - config next to the .app
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            return os.path.join(app_dir, 'JiraExtractor.env')
        else:
            # Other bundled executables - config next to executable
            exe_dir = os.path.dirname(sys.executable)
            return os.path.join(exe_dir, 'JiraExtractor.env')
    else:
        # Running from source - use current directory
        return 'JiraExtractor.env'

def is_port_open(port):
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def open_browser_when_ready(expected_port, max_wait=20):
    """Open browser when the Streamlit server is ready, with robust port detection."""
    print(f"🔍 Looking for Streamlit server...")
    
    # Give Streamlit time to start up
    time.sleep(3)
    
    # Check common Streamlit ports in order of likelihood
    ports_to_try = [3000, 8501, expected_port, 8502, 8503, 3001]
    
    for attempt in range(max_wait):
        for port in ports_to_try:
            if is_port_open(port):
                url = f"http://localhost:{port}"
                print(f"🌍 Found server on port {port}, opening browser...")
                webbrowser.open(url)
                return True
        
        # Wait a bit before trying again
        time.sleep(1)
    
    # If we get here, try to open the most likely ports anyway
    print(f"🔍 Server detection timed out, trying common ports...")
    for port in [3000, 8501]:
        url = f"http://localhost:{port}"
        print(f"🌍 Opening browser at {url} (best guess)")
        webbrowser.open(url)
        time.sleep(2)  # Give user time to see if it works
    
    return False

def main():
    """Run the Streamlit app with automatic browser opening."""
    print("🚀 Starting Jira Data Extractor GUI...")
    print("📊 Streamlit interface will open in your default browser")
    
    # Load environment variables from JiraExtractor.env
    config_file = get_config_file_path()
    load_dotenv(config_file)
    
    # Get port from JiraExtractor.env file or use default
    port = int(os.getenv('STREAMLIT_PORT', '8501'))
    
    # URL where Streamlit will run
    url = f"http://localhost:{port}"
    
    print(f"🌐 Starting on port {port}")
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(
        target=open_browser_when_ready, 
        args=(port,)
    )
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit - simplified approach for packaged executables
    try:
        import streamlit.web.cli as stcli
        
        if getattr(sys, 'frozen', False):
            # Running as packaged executable - avoid port config issues
            print("📦 Running as packaged executable")
            print(f"🌍 Will try to start on port {port}")
            
            # For packaged executables, use minimal config to avoid issues
            sys.argv = [
                "streamlit", "run", "streamlit_app.py",
                "--browser.gatherUsageStats", "false",
                "--server.headless", "false"
            ]
        else:
            # Running from source - full configuration
            print("🐍 Running from source")
            sys.argv = [
                "streamlit", "run", "streamlit_app.py",
                "--server.port", str(port),
                "--server.headless", "false",
                "--server.runOnSave", "true",
                "--browser.gatherUsageStats", "false"
            ]
        
        # Run Streamlit
        stcli.main()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Trying fallback approach...")
        
        # Final fallback - run streamlit without port specification
        try:
            import streamlit.web.cli as stcli
            sys.argv = ["streamlit", "run", "streamlit_app.py"]
            stcli.main()
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            print("💡 Please try running from source: python run_gui.py")

if __name__ == "__main__":
    main()
