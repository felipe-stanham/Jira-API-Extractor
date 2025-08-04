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
        "--onefile",
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
        "--hidden-import", "openpyxl",
        "--hidden-import", "requests",
        "--hidden-import", "python_dotenv",
        "--hidden-import", "streamlit.web.cli",
        "--hidden-import", "streamlit.runtime.scriptrunner.magic_funcs",
        "--collect-all", "streamlit",
        "run_gui.py"
    ]
    
    return run_command(gui_command)

def create_cli_executable():
    """Create standalone CLI executable."""
    print_header("Building CLI Executable")
    
    # Determine platform
    current_platform = platform.system().lower()
    platform_name = 'macos' if current_platform == 'darwin' else 'windows'
    
    # PyInstaller command for CLI
    cli_command = [
        "python3", "-m", "PyInstaller",
        "--onefile",
        "--console",  # Keep console window for CLI
        "--name", f"JiraExtractorCLI_{platform_name}",
        "--add-data", ".env.example:.",
        "--add-data", "chart_colors.py:.",
        "--add-data", "charts_helper_enhanced.py:.",
        "--add-data", "config.py:.",
        "--add-data", "excel_exporter.py:.",
        "--add-data", "jira_api.py:.",
        "--add-data", "utils.py:.",
        "--hidden-import", "openpyxl",
        "--hidden-import", "requests",
        "--hidden-import", "python_dotenv",
        "main.py"
    ]
    
    return run_command(cli_command)

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
    
    # Copy GUI executable
    gui_src = dist_dir / gui_exe
    cli_src = dist_dir / cli_exe
    
    if gui_src.exists():
        shutil.copy2(gui_src, package_dir / ("JiraExtractorGUI.exe" if current_platform == 'windows' else "JiraExtractorGUI"))
        print(f"Copied GUI executable")
    
    if cli_src.exists():
        shutil.copy2(cli_src, package_dir / ("JiraExtractorCLI.exe" if current_platform == 'windows' else "JiraExtractorCLI"))
        print(f"Copied CLI executable")
    
    # Make executables executable on macOS
    if current_platform == 'darwin':
        for exe_file in package_dir.glob("JiraExtractor*"):
            os.chmod(exe_file, 0o755)
    
    # Copy configuration files
    shutil.copy2(".env.example", package_dir / ".env")
    print("Copied .env configuration file")
    
    # Create README for users
    readme_content = f"""# Jira Data Extractor - Standalone Version

## Quick Start

1. **Configure your Jira credentials:**
   - Edit the `.env` file in this folder
   - Add your Jira URL, email, and API token

2. **Run the application:**
   
   ### GUI Version (Recommended for non-technical users):
   {"- Double-click `JiraExtractorGUI.exe`" if current_platform == 'windows' else "- Double-click `JiraExtractorGUI`"}
   - A web interface will open in your browser
   - Fill in the form and click "Run Extraction"
   
   ### Command Line Version:
   {"- Open Command Prompt in this folder" if current_platform == 'windows' else "- Open Terminal in this folder"}
   {"- Run: `JiraExtractorCLI.exe --project YOUR_PROJECT --sprint SPRINT_ID`" if current_platform == 'windows' else "- Run: `./JiraExtractorCLI --project YOUR_PROJECT --sprint SPRINT_ID`"}

## Configuration

Edit the `.env` file with your Jira details:

```
JIRA_API_URL="https://your-domain.atlassian.net"
JIRA_API_TOKEN="your-api-token"
JIRA_USER_EMAIL="your-email@example.com"
```

To get your API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to the `.env` file

## Usage Examples

### GUI Version:
- Just double-click and use the web interface!

### CLI Version:
```bash
# Get issues from a sprint
{"JiraExtractorCLI.exe" if current_platform == 'windows' else "./JiraExtractorCLI"} --project NG --sprint 123

# Get worklogs for a date range
{"JiraExtractorCLI.exe" if current_platform == 'windows' else "./JiraExtractorCLI"} --project NG --start_date 2025-01-01 --end_date 2025-01-31

# Combine both
{"JiraExtractorCLI.exe" if current_platform == 'windows' else "./JiraExtractorCLI"} --project NG --sprint 123 --start_date 2025-01-01 --end_date 2025-01-31
```

## Output

Both versions create an Excel file (`JiraExport.xlsx`) with:
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
    print_header("Jira API Extractor - Standalone Build")
    
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
    
    # Build GUI executable
    if not create_gui_executable():
        print("❌ Failed to build GUI executable")
        return 1
    
    # Build CLI executable
    if not create_cli_executable():
        print("❌ Failed to build CLI executable")
        return 1
    
    # Create distribution package
    if not create_distribution_package():
        print("❌ Failed to create distribution package")
        return 1
    
    print_header("Build Complete!")
    print(f"✅ Successfully built standalone executables for {platform_name}")
    print(f"📦 Distribution package: dist/JiraExtractor_{current_platform}_standalone.zip")
    print("\n🎉 Ready for distribution! Users can:")
    print("   1. Download and unzip the package")
    print("   2. Edit the .env file with their Jira credentials")
    print("   3. Double-click the executable to run")
    print("   4. No Python or dependencies installation required!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
