# Lessons Learned: Bundling Streamlit Apps with PyInstaller

## 📋 Project Overview

**Project:** Jira API Extractor GUI  
**Goal:** Package a Streamlit web application into a standalone macOS .app bundle  
**Tool:** PyInstaller  
**Result:** ✅ **SUCCESSFUL** - Production-ready standalone application  

---

## 🎯 Key Success Factors

### 1. **Proper Working Directory Management**
```python
if hasattr(sys, '_MEIPASS'):
    bundle_dir = sys._MEIPASS
    original_cwd = os.getcwd()
    os.chdir(bundle_dir)  # CRITICAL: Change to bundle directory
    print(f"📁 Changed working directory from {original_cwd} to: {bundle_dir}")
```

**Why This Matters:**
- Streamlit needs to find its files relative to the correct directory
- PyInstaller bundles files in `sys._MEIPASS`, not the original directory
- Without this, Streamlit serves 404 errors for all routes

### 2. **Environment Variables for Static Files**
```python
# Set environment variables for Streamlit static files
os.environ['STREAMLIT_STATIC_PATH'] = bundle_dir
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'true'
```

**Why This Matters:**
- Streamlit's static assets (CSS, JS) need explicit path configuration in bundles
- Default static file serving doesn't work in PyInstaller environments
- These environment variables tell Streamlit where to find its assets

### 3. **Minimal Streamlit Configuration**
```python
# For packaged executables, use minimal configuration to avoid conflicts
sys.argv = [
    "streamlit", "run", app_path,
    "--server.port", str(port),
    "--server.address", "localhost",
    "--browser.gatherUsageStats", "false",
    "--server.headless", "true",  # Don't let Streamlit auto-open browser
    "--global.developmentMode", "false"
]
```

**Why This Matters:**
- Too many configuration options can conflict in packaged environments
- CORS and XSRF protection can cause issues in standalone apps
- Let your own code handle browser opening for better control

---

## 🚨 Critical Issues and Solutions

### Issue 1: Process Explosion (20+ Recursive Processes)

**Problem:**
```python
# ❌ DANGEROUS - Causes infinite recursion in .app bundles
process = subprocess.Popen([sys.executable, "-m", "streamlit", ...])
```

**Root Cause:** 
- `sys.executable` in PyInstaller bundles points to the bundle itself
- Creates recursive subprocess calls that spawn 20+ processes
- Leads to system resource exhaustion

**Solution:**
```python
# ✅ SAFE - Direct execution without subprocess
import streamlit.web.cli as stcli
sys.argv = ["streamlit", "run", app_path, ...]
stcli.main()
```

**Lesson:** Never use subprocess to launch Streamlit from within a PyInstaller bundle.

### Issue 2: Double Browser Tabs

**Problem:**
- Browser opening logic tries multiple ports and opens tabs for each responsive port
- Streamlit also tries to auto-open browser

**Solution:**
```python
# ✅ Single tab approach
def open_browser_when_ready(expected_port, max_wait=20):
    # First, try the expected port (from config)
    for attempt in range(max_wait):
        if is_port_open(expected_port):
            webbrowser.open(f"http://localhost:{expected_port}")
            return True
        time.sleep(1)
    
    # Only try fallback ports if expected port fails
    for port in fallback_ports:
        if is_port_open(port):
            webbrowser.open(f"http://localhost:{port}")
            return True
```

**Lesson:** Use priority-based port checking and disable Streamlit's auto-browser opening.

### Issue 3: 404 Errors in .app Bundle

**Problem:**
- Streamlit server starts but returns 404 for all routes
- Static files (CSS, JS) not found

**Root Causes:**
1. Wrong working directory
2. Streamlit can't find bundled files
3. Static file serving misconfigured

**Solution Stack:**
```python
# 1. Change working directory
os.chdir(sys._MEIPASS)

# 2. Set environment variables
os.environ['STREAMLIT_STATIC_PATH'] = bundle_dir
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'true'

# 3. Use correct app path
app_path = os.path.join(sys._MEIPASS, 'streamlit_app.py')

# 4. Minimal configuration
sys.argv = ["streamlit", "run", app_path, "--server.port", str(port), ...]
```

**Lesson:** Bundle file access requires explicit path management and environment setup.

### Issue 4: Port Mismatch

**Problem:**
- Debug logs show "Server started on port 8501"
- Streamlit output shows "Local URL: http://localhost:3000"
- Browser opens wrong port, gets 404

**Solution:**
```python
# ✅ Explicit port configuration
sys.argv = [
    "streamlit", "run", app_path,
    "--server.port", str(port),  # Force specific port
    "--server.address", "localhost",
    "--server.headless", "true"  # Disable auto-browser opening
]
```

**Lesson:** Always explicitly set the port; don't rely on Streamlit's auto-detection in bundles.

---

## 🛠️ PyInstaller Configuration

### Essential PyInstaller Arguments
```bash
python3 -m PyInstaller \
    --windowed \  # Create .app bundle, not terminal app
    --name JiraExtractorGUI_macos \
    --add-data .env.example:. \  # Include config template
    --add-data streamlit_app.py:. \  # Include main app file
    --hidden-import streamlit \  # Essential imports
    --hidden-import streamlit.web.cli \
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs \
    --hidden-import streamlit.runtime.caching \
    --hidden-import streamlit.runtime.state \
    --collect-all streamlit \  # Collect all Streamlit files
    --collect-all altair \  # If using charts
    --collect-all plotly \  # If using plots
    run_gui.py
```

### Critical Hidden Imports
- `streamlit.web.cli` - Required for `stcli.main()`
- `streamlit.runtime.*` - Core Streamlit functionality
- All chart libraries you use (altair, plotly, etc.)

---

## 🏗️ Recommended Project Structure

```
project/
├── main_app.py              # CLI version (optional)
├── streamlit_app.py         # Streamlit GUI app
├── run_gui.py              # GUI launcher (PyInstaller entry point)
├── config.py               # Configuration management
├── build_executables.py    # Automated build script
├── requirements.txt        # Dependencies
├── .env.example           # Config template
└── ProjectName.env        # Actual config (unique name)
```

### Key Files:

**run_gui.py** (Entry Point):
```python
def main():
    # Load config
    config = load_config()
    port = int(config.get('STREAMLIT_PORT', 8501))
    
    # Handle packaged vs source mode
    if getattr(sys, 'frozen', False):
        # Packaged executable logic
        setup_bundle_environment()
        start_browser_thread(port)
    
    # Run Streamlit
    run_streamlit_safely(port)
```

**Unique Config File Name:**
- Use `ProjectName.env` instead of `.env`
- Allows multiple apps to coexist in same folder
- Easier for users to identify which config belongs to which app

---

## 🧪 Testing Strategy

### 1. **Source Mode Testing**
```bash
python3 run_gui.py
```
**Verify:**
- ✅ Single browser tab opens
- ✅ Correct port from config file
- ✅ All functionality works

### 2. **Bundle Testing**
```bash
dist/AppName.app/Contents/MacOS/AppName
```
**Verify:**
- ✅ No process explosion
- ✅ Browser opens automatically
- ✅ HTTP 200 response from app
- ✅ All static files load correctly

### 3. **Distribution Testing**
- Extract zip file in clean directory
- Double-click .app file
- Configure app through web interface
- Test core functionality

---

## 🔧 Debugging Techniques

### 1. **Check Bundle Contents**
```bash
ls -la dist/AppName.app/Contents/Frameworks/
# Verify streamlit_app.py and dependencies are present
```

### 2. **Test HTTP Accessibility**
```bash
curl -s -w "%{http_code}" http://localhost:8501
# Should return 200 and HTML content
```

### 3. **Monitor Process Count**
```bash
ps aux | grep -i AppName
# Should show only 1-2 processes, not 20+
```

### 4. **Check Working Directory**
```python
print(f"Current working directory: {os.getcwd()}")
print(f"Bundle directory: {getattr(sys, '_MEIPASS', 'Not bundled')}")
```

---

## 📦 Distribution Best Practices

### 1. **Package Structure**
```
AppName_macos_standalone.zip
├── AppName.app              # The executable
├── AppName.env             # Configuration template
└── README.txt              # User instructions
```

### 2. **User Instructions Template**
```markdown
# AppName - Standalone Application

## Quick Start
1. Extract this zip file
2. Double-click AppName.app to launch
3. Configure your settings in the web interface
4. No Python installation required!

## Configuration
Edit AppName.env file to set your preferences before launching.
```

### 3. **Configuration Management**
- Provide template with example values
- Use descriptive variable names
- Include inline comments explaining each setting

---

## ⚠️ Common Pitfalls to Avoid

### 1. **Don't Use Subprocess in Bundles**
```python
# ❌ NEVER DO THIS in PyInstaller bundles
subprocess.Popen([sys.executable, "-m", "streamlit", ...])
```

### 2. **Don't Rely on Default Working Directory**
```python
# ❌ This will fail in bundles
with open("config.json", "r") as f:
    config = json.load(f)

# ✅ Use absolute paths
config_path = os.path.join(sys._MEIPASS, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)
```

### 3. **Don't Over-Configure Streamlit**
```python
# ❌ Too many options can conflict
sys.argv = [
    "streamlit", "run", app_path,
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false",
    "--server.allowRunOnSave", "true",
    # ... many more options
]

# ✅ Keep it minimal
sys.argv = [
    "streamlit", "run", app_path,
    "--server.port", str(port),
    "--server.headless", "true"
]
```

---

## 🎯 Success Metrics

A successfully bundled Streamlit app should achieve:

- ✅ **Single Process Execution** - No process explosion
- ✅ **HTTP 200 Response** - App accessible via curl/browser
- ✅ **Automatic Browser Opening** - No manual URL entry needed
- ✅ **Static Files Loading** - No 404 errors for CSS/JS
- ✅ **Consistent Port Usage** - No port mismatch confusion
- ✅ **Clean Startup/Shutdown** - No hanging processes
- ✅ **User-Friendly Distribution** - Double-click to run

---

## 🚀 For Future LLM Reference

When helping with Streamlit + PyInstaller bundling:

1. **Always check for subprocess usage** - Replace with direct `stcli.main()` calls
2. **Implement working directory changes** - Use `os.chdir(sys._MEIPASS)`
3. **Set Streamlit environment variables** - For static file serving
4. **Use minimal Streamlit configuration** - Avoid option conflicts
5. **Implement proper browser opening logic** - Single tab, port priority
6. **Test both source and bundle modes** - Ensure consistency
7. **Create unique config file names** - Avoid `.env` conflicts

The key insight is that **PyInstaller bundles behave very differently from source code execution**, especially regarding:
- File paths and working directories
- Process execution and subprocess calls
- Static file serving and web server configuration
- Environment variable inheritance

Always test the bundle extensively and expect to need bundle-specific code paths for proper functionality.

---

## 🔄 Automatic Shutdown & Heartbeat Mechanism

### Problem: Zombie Processes
**Challenge:** Streamlit apps continue running indefinitely after browser closes, creating zombie processes that consume system resources.

### Solution: Background Heartbeat with Auto-Shutdown

#### 1. **Hidden Button + JavaScript Approach**
```python
# In sidebar or main area
def dummy_heartbeat():
    """Dummy function called by JavaScript heartbeat to keep app alive."""
    print(f"💓 Background heartbeat triggered at {time.time()}")
    update_activity()
    return True

# Hidden heartbeat button that JavaScript will click
if st.button("💓", key="bg_heartbeat", help="Background heartbeat (hidden)", type="primary"):
    dummy_heartbeat()
```

#### 2. **JavaScript Auto-Clicker**
```javascript
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
        heartbeatButton.style.display = 'none';  // Hide the button
        heartbeatButton.click();
        console.log('💓 Heartbeat button clicked successfully');
    } else {
        console.log('⚠️ Heartbeat button not found');
    }
}

// Click heartbeat button every 1 minute (60000 ms)
setInterval(clickHeartbeatButton, 60000);

// Click initial heartbeat after 1 second
setTimeout(clickHeartbeatButton, 1000);

console.log('💓 Background heartbeat initialized - will trigger every 60 seconds');
</script>
"""

# Inject the JavaScript
components.html(heartbeat_js, height=0)
```

#### 3. **Shared Timestamp File for Thread Coordination**
```python
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
```

#### 4. **Background Monitoring Thread**
```python
def check_for_inactivity_simple():
    """Monitor activity using shared timestamp file with efficient thread management."""
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
            
            # If no activity for INACTIVITY_TIMEOUT seconds, shutdown
            if time_since_activity > INACTIVITY_TIMEOUT:
                print(f"🕐 Thread {thread_id} - No browser activity for {time_since_activity:.0f} seconds. Auto-shutting down...")
                os._exit(0)
                
        except Exception as e:
            print(f"Thread {thread_id} error: {e}")
            pass
```

#### 5. **Efficient Thread Management**
```python
def is_monitoring_thread_active():
    """Check if a monitoring thread is already active by checking the timestamp file age."""
    import tempfile
    import time
    
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

# Start heartbeat monitoring thread only if none is active
if not is_monitoring_thread_active():
    mark_monitoring_active()
    heartbeat_thread = threading.Thread(target=check_for_inactivity_simple, daemon=True)
    heartbeat_thread.start()
    print("Started heartbeat monitoring thread")
else:
    print("Monitoring thread already active - skipping thread creation")
```

### Key Insights:

1. **✅ JavaScript Heartbeat Works**: Hidden button + JS auto-clicker reliably keeps app alive
2. **✅ Shared Timestamp Files**: Enable thread coordination across Streamlit reruns
3. **✅ Thread Optimization**: Prevent multiple monitoring threads with file-based coordination
4. **✅ 5-Minute Timeout**: Reasonable balance between usability and resource management
5. **✅ Invisible Operation**: Users don't see heartbeat mechanism, clean UI experience

### Behavior:
- **Browser Open**: JavaScript clicks heartbeat button every 60 seconds → app stays alive indefinitely
- **Browser Closed**: No JavaScript activity → app shuts down after 5 minutes of inactivity
- **Page Reloads**: New threads created but coordinate via shared files, no conflicts
- **User Interactions**: Don't interfere with shutdown mechanism, heartbeat runs independently

---

## 📁 Configuration File Management

### Problem: Config File Location and Naming
**Challenge:** Multiple apps in same folder, hidden `.env` files, user confusion about config location.

### Solution: Unique Named Config Files

#### 1. **Use App-Specific Config Names**
```python
def get_config_file_path():
    """Get the path for the user's JiraExtractor.env file, handling bundled executables."""
    # For bundled executables, save config in the same directory as the executable
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        bundle_dir = os.path.dirname(sys.executable)
        return os.path.join(bundle_dir, 'JiraExtractor.env')  # NOT .env
    else:
        # Running from source
        return os.path.join(os.getcwd(), 'JiraExtractor.env')
```

#### 2. **Config File Location by Mode**

**Source Mode:**
- Config file: `./JiraExtractor.env` (in project directory)
- Template: `./JiraExtractor.env.example` (if provided)

**Bundled Mode (.app):**
- Config file: `JiraExtractor.env` (same directory as .app bundle)
- Template: Not included in bundle (app creates config automatically)

#### 3. **Auto-Creation with Sensible Defaults**
```python
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
```

### Key Insights:

1. **✅ Unique Names**: `JiraExtractor.env` instead of `.env` prevents conflicts
2. **✅ Visible Files**: Not hidden, easier for users to find and edit
3. **✅ Location Awareness**: Different paths for source vs bundled modes
4. **✅ Auto-Creation**: App creates config file automatically on first run
5. **✅ No Templates in Bundle**: Reduces bundle size, app handles defaults

### Config File Locations:
```
# Source Mode
project/
├── streamlit_app.py
├── run_gui.py
└── JiraExtractor.env          # ← Config file here

# Bundled Mode
user_folder/
├── JiraExtractor.app          # ← App bundle
└── JiraExtractor.env          # ← Config file here (same level)
```

---

## 📚 Additional Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Streamlit Configuration Reference](https://docs.streamlit.io/library/advanced-features/configuration)
- [macOS App Bundle Guidelines](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html)
- [JavaScript setInterval Documentation](https://developer.mozilla.org/en-US/docs/Web/API/setInterval)
- [Python Threading Documentation](https://docs.python.org/3/library/threading.html)

---

**Created:** 2025-08-05  
**Updated:** 2025-08-06  
**Project:** Jira API Extractor  
**Status:** ✅ Production Ready with Auto-Shutdown  
**Next:** Consider Windows packaging with similar principles
