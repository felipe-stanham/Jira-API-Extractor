"""Configuration module for Jira API Extractor."""

import os
import sys
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

# Load environment variables from JiraExtractor.env file
config_file = get_config_file_path()
load_dotenv(config_file)

# Jira API credentials from environment variables
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")

def get_auth():
    """Returns the authentication object for Jira API requests."""
    return (JIRA_USER_EMAIL, JIRA_API_TOKEN)

def validate_config():
    """Validates that all required configuration is present."""
    if not JIRA_API_URL:
        raise ValueError("JIRA_API_URL is not set in environment variables")
    if not JIRA_API_TOKEN:
        raise ValueError("JIRA_API_TOKEN is not set in environment variables")
    if not JIRA_USER_EMAIL:
        raise ValueError("JIRA_USER_EMAIL is not set in environment variables")
