"""Configuration module for Jira API Extractor."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
