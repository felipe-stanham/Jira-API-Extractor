#!/usr/bin/env python3
"""
Build script for creating standalone executables of Jira API Extractor.

This script creates double-click executables for Mac and Windows that include
all dependencies and don't require Python installation.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(f" {message}".upper())
    print("=" * 60)

def run_command(command, cwd=None):
    """Run a shell command and return success status."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print("Error output:")
            print(e.stderr)
        return False

def clean_build_dirs():
    """Clean previous build directories."""
    print("Cleaning previous build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")

def create_gui_executable():
    """Create standalone GUI executable."""
    print_header("Building GUI Executable")
    
    # Determine platform
    current_platform = platform.system().lower()
    platform_name = 'macos' if current_platform == 'darwin' else 'windows'
    
    # PyInstaller command for GUI
    gui_command = [
        "python3", "-m", "PyInstaller",
        "--windowed",  # No console window for GUI
        "--name", f"JiraExtractorGUI_{platform_name}",
        "--add-data", ".env.example:.",
        "--add-data", "chart_colors.py:.",
        "--add-data", "charts_helper_enhanced.py:.",
        "--add-data", "config.py:.",
        "--add-data", "excel_exporter.py:.",
        "--add-data", "jira_api.py:.",
        "--add-data", "utils.py:.",
        "--add-data", "main.py:.",
        "--add-data", "streamlit_app.py:.",
        "--hidden-import", "streamlit",
        "--hidden-import", "streamlit.web.cli",
        "--hidden-import", "streamlit.runtime.scriptrunner.magic_funcs",
        "--hidden-import", "streamlit.runtime.caching",
        "--hidden-import", "streamlit.runtime.state",
        "--hidden-import", "openpyxl",
        "--hidden-import", "requests",
        "--hidden-import", "python_dotenv",
        "--collect-all", "streamlit",
        "--collect-all", "altair",
        "--collect-all", "plotly",
        "run_gui.py"
    ]
    
    # For macOS, remove --onefile to create .app bundle instead of single executable
    if current_platform != 'darwin':
        gui_command.insert(3, "--onefile")
    
    return run_command(gui_command)

# CLI executable removed - users can install dependencies if they need CLI access

def create_distribution_package():
    """Create a distribution package with executables and documentation."""
    print_header("Creating Distribution Package")
    
    current_platform = platform.system().lower()
    platform_name = 'macos' if current_platform == 'darwin' else 'windows'
    
    # Create distribution directory
    dist_dir = Path("dist")
    package_dir = dist_dir / f"JiraExtractor_{platform_name}"
    package_dir.mkdir(exist_ok=True)
    
    # Copy executables
    gui_exe = f"JiraExtractorGUI_{platform_name}"
    cli_exe = f"JiraExtractorCLI_{platform_name}"
    
    if current_platform == 'windows':
        gui_exe += ".exe"
        cli_exe += ".exe"
    
    # Copy GUI executable to package directory
    if current_platform == 'darwin':
        # For macOS, copy the entire .app bundle
        gui_app_src = dist_dir / f"JiraExtractorGUI_{platform_name}.app"
        if gui_app_src.exists():
            shutil.copytree(gui_app_src, package_dir / f"JiraExtractorGUI_{platform_name}.app")
            print(f"Copied GUI app bundle: {gui_app_src.name}")
    else:
        # For Windows, copy the executable file
        gui_src = dist_dir / f"JiraExtractorGUI_{platform_name}.exe"
        if gui_src.exists():
            shutil.copy2(gui_src, package_dir / "JiraExtractorGUI.exe")
            print(f"Copied GUI executable: {gui_src.name}")
    
    # Make executables executable on macOS
    if current_platform == 'darwin':
        for exe_file in package_dir.glob("JiraExtractor*"):
            os.chmod(exe_file, 0o755)
    
    # Copy .env.example as JiraExtractor.env for user configuration
    shutil.copy2(".env.example", package_dir / "JiraExtractor.env")
    print("Copied JiraExtractor.env configuration file")
    
    # Create README for users
    readme_content = f"""# Jira Data Extractor - GUI Application

## Quick Start

1. **Run the application:**
   {"- Double-click `JiraExtractorGUI_windows.exe`" if current_platform == 'windows' else "- Double-click `JiraExtractorGUI_macos.app`"}
   - A web interface will open in your browser automatically
   - Configure your Jira credentials in the sidebar
   - Fill in the extraction form and click "Run Extraction"

2. **First-time setup:**
   - The app will prompt you to enter your Jira credentials
   - Your settings will be saved to `JiraExtractor.env` for future use

## Configuration

The app will create a `JiraExtractor.env` file with your Jira details:

```
JIRA_API_URL="https://your-domain.atlassian.net"
JIRA_API_TOKEN="your-api-token"
JIRA_USER_EMAIL="your-email@example.com"
```

To get your API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Enter it in the app's configuration sidebar

## Usage

1. **Double-click the app** to launch
2. **Configure credentials** in the sidebar (first time only)
3. **Enter project details:**
   - Project code (e.g., "NG")
   - Sprint IDs (comma-separated, e.g., "123,124")
   - Or date range for worklogs
4. **Click "Run Extraction"** and wait for completion
5. **Download the Excel file** when ready

## Output

The app creates an Excel file (`JiraExport.xlsx`) with:
- Sprint Issues sheet
- Work Logs sheet  
- Comments sheet
- Charts sheet with visualizations

## No Installation Required!

This package includes everything needed to run the Jira Data Extractor:
- Python runtime
- All required libraries (Streamlit, openpyxl, requests, etc.)
- The complete application

Just configure the `.env` file and run!

---
Jira Data Extractor v1.1 - Built with ❤️
"""
    
    with open(package_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    print("Created README.txt")
    
    # Create a zip archive
    archive_name = f"JiraExtractor_{platform_name}_standalone"
    print(f"Creating zip archive: {archive_name}.zip")
    
    shutil.make_archive(
        str(dist_dir / archive_name), 
        'zip', 
        dist_dir, 
        f"JiraExtractor_{platform_name}"
    )
    
    print(f"\n✅ Distribution package created: dist/{archive_name}.zip")
    return True

def main():
    """Main build function."""
    print_header("Jira API Extractor - GUI Build")
    
    # Check platform
    current_platform = platform.system().lower()
    if current_platform not in ['darwin', 'windows']:
        print(f"❌ Unsupported platform: {current_platform}")
        print("This script supports macOS and Windows only.")
        return 1
    
    platform_name = 'macOS' if current_platform == 'darwin' else 'Windows'
    print(f"🖥️  Building for: {platform_name}")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build GUI executable only
    if not create_gui_executable():
        print("❌ GUI build failed")
        return 1
    
    # Create distribution package
    if not create_distribution_package():
        print("❌ Failed to create distribution package")
        return 1
    
    print_header("Build Complete!")
    print(f"✅ Successfully built GUI executable for {platform_name}")
    
    if current_platform == 'darwin':
        print(f"📱 macOS App Bundle: dist/JiraExtractorGUI_macos.app")
        print("\n🎉 Ready for distribution! Users can:")
        print("   1. Double-click the .app file to run")
        print("   2. Configure Jira credentials in the app")
        print("   3. No Python or dependencies installation required!")
    else:
        print(f"💻 Windows Executable: dist/JiraExtractorGUI_windows.exe")
        print("\n🎉 Ready for distribution! Users can:")
        print("   1. Double-click the .exe file to run")
        print("   2. Configure Jira credentials in the app")
        print("   3. No Python or dependencies installation required!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
