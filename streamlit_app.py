#!/usr/bin/env python3
"""
Jira API Extractor - Streamlit GUI

A simple web-based user interface for the Jira API Extractor using Streamlit.
"""

import streamlit as st
import os
import sys
import subprocess
import threading
import time
from datetime import datetime, timedelta
from io import StringIO
import webbrowser
import atexit

# Global variables for heartbeat mechanism (thread-safe)
import threading
last_activity_lock = threading.Lock()
last_activity_time = time.time()

# Efficient thread management - check if monitoring thread already exists
import tempfile
import os

def is_monitoring_thread_active():
    """Check if a monitoring thread is already active by checking the timestamp file age."""
    import tempfile
    import time
    
    timestamp_file = os.path.join(tempfile.gettempdir(), 'jira_extractor_last_activity.txt')
    monitor_file = os.path.join(tempfile.gettempdir(), 'jira_extractor_monitor_active.txt')
    
    try:
        # Check if monitor file exists and is recent (within last 15 seconds)
        if os.path.exists(monitor_file):
            with open(monitor_file, 'r') as f:
                last_monitor_time = float(f.read().strip())
            
            if time.time() - last_monitor_time < 15:
                return True
    except:
        pass
    
    return False

def mark_monitoring_active():
    """Mark that a monitoring thread is active."""
    import tempfile
    import time
    
    monitor_file = os.path.join(tempfile.gettempdir(), 'jira_extractor_monitor_active.txt')
    try:
        with open(monitor_file, 'w') as f:
            f.write(str(time.time()))
    except:
        pass

def start_heartbeat_thread_once():
    """Start heartbeat thread - all threads monitor independently using shared timestamp."""
    # Start heartbeat monitoring thread only if none is active
    if not is_monitoring_thread_active():
        mark_monitoring_active()
        heartbeat_thread = threading.Thread(target=check_for_inactivity_simple, daemon=True)
        heartbeat_thread.start()
        print("Started heartbeat monitoring thread")
    else:
        print("Monitoring thread already active - skipping thread creation")
        return True

def check_for_inactivity_simple():
    """Simple approach - monitor activity using shared timestamp file with efficient thread management."""
    import time
    import os
    
    # Wait 5 minutes of inactivity before auto-shutdown
    INACTIVITY_TIMEOUT = 300  # 5 minutes (300 seconds)
    thread_id = threading.current_thread().ident
    
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        try:
            # Mark this thread as active monitoring thread
            mark_monitoring_active()
            
            # Read last activity time from shared file
            timestamp_file = os.path.join(tempfile.gettempdir(), 'jira_extractor_last_activity.txt')
            
            if os.path.exists(timestamp_file):
                with open(timestamp_file, 'r') as f:
                    last_activity_from_file = float(f.read().strip())
            else:
                last_activity_from_file = time.time()  # If no file, assume recent activity
            
            time_since_activity = time.time() - last_activity_from_file
            print(f"Thread {thread_id} - last_activity_from_file: {last_activity_from_file}")
            print(f"Thread {thread_id} - Time since activity: {time_since_activity:.1f} seconds")
            
            # If no activity for INACTIVITY_TIMEOUT seconds, shutdown
            if time_since_activity > INACTIVITY_TIMEOUT:
                print(f"🕐 Thread {thread_id} - No browser activity for {time_since_activity:.0f} seconds. Auto-shutting down...")
                os._exit(0)
                
        except Exception as e:
            print(f"Thread {thread_id} error: {e}")
            pass

# Configure Streamlit page
st.set_page_config(
    page_title="Jira Data Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Heartbeat mechanism - update activity timestamp (shared file)
def update_activity():
    """Update activity timestamp in shared file so all threads can see it."""
    import tempfile
    import os
    
    current_time = time.time()
    timestamp_file = os.path.join(tempfile.gettempdir(), 'jira_extractor_last_activity.txt')
    
    try:
        with open(timestamp_file, 'w') as f:
            f.write(str(current_time))
        print(f"Activity updated: {current_time}")
    except Exception as e:
        print(f"Error updating activity: {e}")
        pass
    
    # Also update global variable for backward compatibility
    global last_activity_time
    with last_activity_lock:
        last_activity_time = current_time

update_activity()

# Original check_for_inactivity function removed - now using check_for_inactivity_coordinated

# Start heartbeat monitoring thread (only once per process using file lock)
start_heartbeat_thread_once()

# Always update activity on every page load/refresh
update_activity()

def get_config_file_path():
    """Get the path for the user's JiraExtractor.env file, handling bundled executables."""
    # For bundled executables, save config in the same directory as the executable
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        if sys.platform == 'darwin' and '.app' in sys.executable:
            # macOS .app bundle - save config next to the .app
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            return os.path.join(app_dir, 'JiraExtractor.env')
        else:
            # Other bundled executables - save next to executable
            exe_dir = os.path.dirname(sys.executable)
            return os.path.join(exe_dir, 'JiraExtractor.env')
    else:
        # Running from source - use current directory
        return 'JiraExtractor.env'

def load_bundled_template():
    """Load the bundled .env.example template."""
    config = {}
    template_paths = ['.env.example', 'env.example']  # Try multiple locations
    
    for template_path in template_paths:
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            # Only load non-placeholder values
                            value = value.strip('"').strip("'")
                            if not value.startswith('your-') and value != 'your-api-token':
                                config[key] = value
                break
            except Exception:
                continue
    return config

def load_config():
    """Load configuration from user's JiraExtractor.env file or bundled template."""
    config_path = get_config_file_path()
    config = {}
    
    # First, try to load user's saved config
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value.strip('"').strip("'")
        except Exception as e:
            st.warning(f"Could not load saved config: {e}")
    
    # If no user config, try to load from bundled template
    if not config:
        config = load_bundled_template()
    
    return config

def save_config(url, email, token):
    """Save configuration to user's JiraExtractor.env file."""
    config_path = get_config_file_path()
    
    try:
        # Ensure the directory exists (only if there's a directory path)
        config_dir = os.path.dirname(config_path)
        if config_dir:  # Only create directory if path has a directory component
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(f'JIRA_API_URL="{url}"\n')
            f.write(f'JIRA_USER_EMAIL="{email}"\n')
            f.write(f'JIRA_API_TOKEN="{token}"\n')
            
            # Add optional port setting if it exists in environment
            if 'STREAMLIT_PORT' in os.environ:
                f.write(f'STREAMLIT_PORT={os.environ["STREAMLIT_PORT"]}\n')
        
        return True
    except Exception as e:
        st.error(f"Failed to save configuration: {str(e)}")
        st.error(f"Attempted to save to: {config_path}")
        return False

def run_extraction(project, sprint_ids, start_date, end_date, progress_placeholder, log_placeholder):
    """Run the Jira data extraction with progress updates."""
    
    # Prepare command
    cmd = [sys.executable, "main.py", "--project", project]
    
    if sprint_ids:
        cmd.extend(["--sprint", sprint_ids])
    
    if start_date and end_date:
        cmd.extend([
            "--start_date", start_date.strftime("%Y-%m-%d"),
            "--end_date", end_date.strftime("%Y-%m-%d")
        ])
    
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.strip())
                # Update the log display
                log_placeholder.text_area(
                    "Extraction Log:",
                    value="\n".join(output_lines),
                    height=200,
                    key=f"log_{len(output_lines)}"
                )
                
                # Update progress based on keywords in output
                if "Fetching issues" in line:
                    progress_placeholder.progress(0.2, "Fetching sprint issues...")
                elif "Fetching work logs" in line:
                    progress_placeholder.progress(0.5, "Fetching work logs...")
                elif "Fetching comments" in line:
                    progress_placeholder.progress(0.7, "Fetching comments...")
                elif "Saving data to Excel" in line:
                    progress_placeholder.progress(0.9, "Generating Excel file...")
                elif "Export complete" in line:
                    progress_placeholder.progress(1.0, "✅ Export completed successfully!")
        
        process.wait()
        
        if process.returncode == 0:
            return True, "\n".join(output_lines)
        else:
            return False, "\n".join(output_lines)
            
    except Exception as e:
        return False, f"Error running extraction: {str(e)}"

def main():
    """Main Streamlit application."""
    
    # JavaScript heartbeat to keep server alive while browser is open
    import streamlit.components.v1 as components
    
    # Background heartbeat mechanism - hidden button + JavaScript
    def dummy_heartbeat():
        """Dummy function called by JavaScript heartbeat to keep app alive."""
        print(f"💓 Background heartbeat triggered at {time.time()}")
        update_activity()
        return True
    
    # JavaScript to click heartbeat button every 1 minute
    heartbeat_js = """
    <script>
    function clickHeartbeatButton() {
        console.log('💓 Searching for heartbeat button...');
        
        // Find the heartbeat button by looking for the heart emoji
        const buttons = parent.document.querySelectorAll('button');
        let heartbeatButton = null;
        
        for (let button of buttons) {
            if (button.textContent.includes('💓')) {
                heartbeatButton = button;
                break;
            }
        }
        
        if (heartbeatButton) {
            heartbeatButton.click();
            console.log('💓 Heartbeat button clicked successfully');
        } else {
            console.log('⚠️ Heartbeat button not found');
        }
    }
    
    // Click heartbeat button every 1 minute (60000 ms)
    setInterval(clickHeartbeatButton, 60000);
    
    // Click initial heartbeat after 5 seconds
    setTimeout(clickHeartbeatButton, 5000);
    
    console.log('💓 Background heartbeat initialized - will trigger every 60 seconds');
    </script>
    """
    
    # Inject the JavaScript
    components.html(heartbeat_js, height=0)
    
    # Hidden heartbeat button that JavaScript will click every minute
    if st.button("💓", key="bg_heartbeat", help="Background heartbeat (hidden)", type="primary"):
        dummy_heartbeat()
        st.success("💓 Heartbeat received - app will stay alive for 5 more minutes", icon="✅")
    
    # Header (timer removed - using background heartbeat instead)
    st.title("📊 Jira Data Extractor")
    st.markdown("Extract Jira data including sprint issues, worklogs, and comments to Excel with rich visualizations.")
    
    # Load existing configuration
    config = load_config()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Jira Configuration
        st.subheader("Jira Settings")
        
        jira_url = st.text_input(
            "Jira URL",
            value=config.get('JIRA_API_URL', ''),
            placeholder="https://your-domain.atlassian.net",
            help="Your Jira instance URL"
        )
        
        jira_email = st.text_input(
            "Email",
            value=config.get('JIRA_USER_EMAIL', ''),
            placeholder="your-email@example.com",
            help="The email address you use to log in to Jira"
        )
        
        jira_token = st.text_input(
            "API Token",
            value=config.get('JIRA_API_TOKEN', ''),
            type="password",
            placeholder="Your Jira API token",
            help="Generate one at: https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        
        # Save configuration button
        if st.button("💾 Save Configuration", use_container_width=True):
            if jira_url and jira_email and jira_token:
                if save_config(jira_url, jira_email, jira_token):
                    config_path = get_config_file_path()
                    st.success("✅ Configuration saved!")
                    st.info(f"📁 Saved to: {os.path.basename(config_path)}")
                    st.info(f"📍 Location: {os.path.abspath(config_path)}")
                    st.rerun()
            else:
                st.error("❌ Please fill in all configuration fields")
        
        # Configuration status
        config_path = get_config_file_path()
        if jira_url and jira_email and jira_token:
            if os.path.exists(config_path):
                st.success("✅ Configuration complete")
                st.info(f"📁 Config file: {os.path.basename(config_path)}")
            else:
                st.warning("⚠️ Configuration complete but not saved. Click 'Save Configuration' to persist settings.")
        else:
            if os.path.exists(config_path):
                st.info(f"📝 Found existing config: {os.path.basename(config_path)}")
            else:
                st.warning("⚠️ Please configure your Jira settings")
        
        # Shutdown section
        st.markdown("---")
        st.markdown("### 🔴 App Control")
        if st.button("🛑 Shutdown App", use_container_width=True, type="secondary"):
            st.warning("🔄 Shutting down application...")
            st.info("You can close this browser tab now.")
            # Give the UI time to update before shutdown
            time.sleep(1)
            # Graceful shutdown
            os._exit(0)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Extraction Parameters")
        
        # Project Key
        project_key = st.text_input(
            "Project Key",
            value="",
            placeholder="e.g., NG",
            help="The key for your Jira project"
        ).upper()
        
        # Sprint IDs
        sprint_ids = st.text_input(
            "Sprint ID(s)",
            value="",
            placeholder="e.g., 123 or 123,456,789",
            help="Comma-separated list of sprint IDs (optional)"
        )
        
        st.subheader("📅 Date Range (Optional)")
        st.markdown("*Use date range to extract worklogs and comments*")
        
        # Initialize session state for dates if not exists
        if 'quick_start_date' not in st.session_state:
            st.session_state['quick_start_date'] = None
        if 'quick_end_date' not in st.session_state:
            st.session_state['quick_end_date'] = None
        
        # Date inputs with date picker
        col_start, col_end = st.columns(2)
        
        with col_start:
            start_date = st.date_input(
                "Start Date",
                value=st.session_state['quick_start_date'],
                help="Start date for worklogs and comments",
                key="start_date_input"
            )
        
        with col_end:
            end_date = st.date_input(
                "End Date",
                value=st.session_state['quick_end_date'],
                help="End date for worklogs and comments",
                key="end_date_input"
            )
        
        # Quick date range buttons
        st.markdown("**Quick Select:**")
        col_week, col_month = st.columns(2)
        
        with col_week:
            if st.button("📅 Last Week", use_container_width=True):
                end_date_calc = datetime.now() - timedelta(days=datetime.now().weekday() + 1)
                start_date_calc = end_date_calc - timedelta(days=6)
                st.session_state['quick_start_date'] = start_date_calc.date()
                st.session_state['quick_end_date'] = end_date_calc.date()
                st.rerun()
        
        with col_month:
            if st.button("📅 Last Month", use_container_width=True):
                today = datetime.now()
                first_day_of_month = today.replace(day=1)
                end_date_calc = first_day_of_month - timedelta(days=1)
                start_date_calc = end_date_calc.replace(day=1)
                st.session_state['quick_start_date'] = start_date_calc.date()
                st.session_state['quick_end_date'] = end_date_calc.date()
                st.rerun()
    
    with col2:
        st.header("🚀 Extraction")
        
        # Validation
        can_run = True
        validation_messages = []
        
        if not jira_url or not jira_email or not jira_token:
            can_run = False
            validation_messages.append("❌ Please configure Jira settings in the sidebar")
        
        if not project_key:
            can_run = False
            validation_messages.append("❌ Project Key is required")
        
        if not sprint_ids and not (start_date and end_date):
            can_run = False
            validation_messages.append("❌ Please provide either Sprint ID(s) or Date Range")
        
        if (start_date and not end_date) or (not start_date and end_date):
            can_run = False
            validation_messages.append("❌ Both start and end dates are required")
        
        # Show validation messages
        if validation_messages:
            for msg in validation_messages:
                st.error(msg)
        else:
            st.success("✅ Ready to extract data")
        
        # Run button
        if st.button("🚀 Run Extraction", disabled=not can_run, use_container_width=True, type="primary"):
            if can_run:
                # Initialize progress and log areas
                progress_placeholder = st.empty()
                log_placeholder = st.empty()
                
                progress_placeholder.progress(0.1, "🔄 Starting extraction...")
                
                # Run extraction
                success, output = run_extraction(
                    project_key, 
                    sprint_ids, 
                    start_date, 
                    end_date,
                    progress_placeholder,
                    log_placeholder
                )
                
                if success:
                    st.success("🎉 Extraction completed successfully!")
                    
                    # Check if Excel file was created
                    if os.path.exists("JiraExport.xlsx"):
                        st.info("📁 Excel file created: JiraExport.xlsx")
                        
                        # Offer download
                        with open("JiraExport.xlsx", "rb") as file:
                            st.download_button(
                                label="📥 Download Excel File",
                                data=file.read(),
                                file_name=f"JiraExport_{project_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                else:
                    st.error("❌ Extraction failed. Check the log for details.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Jira Data Extractor v1.0 | Built with ❤️ using Streamlit</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Auto-open browser (this works when running with streamlit run)
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # This is handled by Streamlit's built-in browser opening
        pass
    
    main()
