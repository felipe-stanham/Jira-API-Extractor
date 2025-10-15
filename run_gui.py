#!/usr/bin/env python3
"""
Streamlit GUI Runner for Jira API Extractor

This script runs the Streamlit GUI on the port specified in JiraExtractor.env
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    """Main entry point for the GUI launcher."""
    print("🚀 Starting Jira Data Extractor GUI...")
    
    # Load environment variables from JiraExtractor.env
    config_file = 'JiraExtractor.env'
    load_dotenv(config_file)
    
    # Get port from JiraExtractor.env file or use default
    port = os.getenv('STREAMLIT_PORT', '8501')
    
    print(f"🌐 Starting Streamlit on port {port}")
    print(f"📊 Streamlit interface will open in your default browser")
    print(f"🛑 Press Ctrl+C to stop the server")
    
    # Build the streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "streamlit_app.py",
        "--server.port", str(port),
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        # Run streamlit
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("📝 Please ensure Streamlit is installed: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
