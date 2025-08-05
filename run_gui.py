#!/usr/bin/env python3
"""
Streamlit GUI Runner for Jira API Extractor

This script runs the Streamlit GUI and automatically opens the browser.
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
import socket
import signal
import atexit
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
    """Open browser when the Streamlit server is ready, with single tab opening."""
    print(f"🔍 Looking for Streamlit server on port {expected_port}...")
    
    # Give Streamlit time to start up
    time.sleep(3)
    
    # First, try the expected port (from config)
    for attempt in range(max_wait):
        if is_port_open(expected_port):
            url = f"http://localhost:{expected_port}"
            print(f"🌍 Found server on expected port {expected_port}, opening browser...")
            webbrowser.open(url)
            return True
        time.sleep(1)
    
    # If expected port doesn't work, try common Streamlit defaults
    print(f"🔍 Expected port {expected_port} not responding, trying defaults...")
    fallback_ports = [8501, 3000] if expected_port not in [8501, 3000] else [3000, 8501]
    
    for port in fallback_ports:
        if is_port_open(port):
            url = f"http://localhost:{port}"
            print(f"🌍 Found server on fallback port {port}, opening browser...")
            webbrowser.open(url)
            return True
    
    # Last resort - open expected port anyway
    url = f"http://localhost:{expected_port}"
    print(f"🌍 Opening browser at {url} (last resort)")
    webbrowser.open(url)
    return False

# Global variable to track Streamlit process
streamlit_process = None

def cleanup_streamlit():
    """Clean up Streamlit process on app exit."""
    global streamlit_process
    if streamlit_process:
        print("🧹 Cleaning up Streamlit process...")
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
        except:
            try:
                streamlit_process.kill()
            except:
                pass
        streamlit_process = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    cleanup_streamlit()
    sys.exit(0)

def setup_signal_handlers():
    """Set up signal handlers for clean shutdown."""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination
    atexit.register(cleanup_streamlit)  # Cleanup on normal exit

def run_streamlit_safely(port):
    """Run Streamlit safely without subprocess recursion issues."""
    try:
        import streamlit.web.cli as stcli
        
        if getattr(sys, 'frozen', False):
            # Running as packaged executable - use robust configuration
            print("📦 Running as packaged executable")
            print(f"🌍 Starting Streamlit on port {port}")
            
            # Get the correct path to streamlit_app.py in the bundle
            import os
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle - set up environment for Streamlit
                bundle_dir = sys._MEIPASS
                app_path = os.path.join(bundle_dir, 'streamlit_app.py')
                
                # Set environment variables for Streamlit static files
                os.environ['STREAMLIT_STATIC_PATH'] = bundle_dir
                os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'true'
                
                # Change to bundle directory to ensure relative imports work
                original_cwd = os.getcwd()
                os.chdir(bundle_dir)
                print(f"📁 Changed working directory from {original_cwd} to: {bundle_dir}")
            else:
                app_path = 'streamlit_app.py'
            
            print(f"📁 Using app path: {app_path}")
            
            # For packaged executables, use minimal configuration to avoid conflicts
            sys.argv = [
                "streamlit", "run", app_path,
                "--server.port", str(port),
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true",  # Don't let Streamlit auto-open browser
                "--global.developmentMode", "false"
            ]
        else:
            # Running from source - use configured port
            print("🐍 Running from source")
            print(f"🌍 Starting on configured port {port}")
            sys.argv = [
                "streamlit", "run", "streamlit_app.py",
                "--server.port", str(port),
                "--server.headless", "false",
                "--server.runOnSave", "true",
                "--browser.gatherUsageStats", "false"
            ]
        
        # Run Streamlit directly
        stcli.main()
        return True
        
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return False

def main():
    """Main entry point for the GUI launcher."""
    print("🚀 Starting Jira Data Extractor GUI...")
    print("📊 Streamlit interface will open in your default browser")
    
    # Set up signal handlers for clean shutdown
    setup_signal_handlers()
    
    # Load environment variables from JiraExtractor.env
    config_file = get_config_file_path()
    load_dotenv(config_file)
    
    # Get port from JiraExtractor.env file or use default
    port = int(os.getenv('STREAMLIT_PORT', '8501'))
    print(f"🌐 Starting on port {port}")
    
    # For packaged executables, start browser opening in background
    if getattr(sys, 'frozen', False):
        browser_thread = threading.Thread(
            target=open_browser_when_ready, 
            args=(port,)
        )
        browser_thread.daemon = True
        browser_thread.start()
    
    # Run Streamlit safely
    try:
        if not run_streamlit_safely(port):
            print("💡 Trying fallback approach...")
            # Fallback to the old method
            import streamlit.web.cli as stcli
            sys.argv = ["streamlit", "run", "streamlit_app.py"]
            stcli.main()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("📝 Please run 'python3 streamlit_app.py' manually")

if __name__ == "__main__":
    main()
