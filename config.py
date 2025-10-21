"""Configuration module for Jira API Extractor."""

import os
import sys
from dotenv import load_dotenv

def get_config_file_path():
    """Get the path for JiraExtractor.env file."""
    return 'JiraExtractor.env'

# Load environment variables from JiraExtractor.env file
config_file = get_config_file_path()
load_dotenv(config_file)

# Jira API credentials from environment variables
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")

# Story Points custom field (varies by Jira instance)
# Common values: customfield_10016, customfield_10026
JIRA_STORY_POINTS_FIELD = os.getenv("JIRA_STORY_POINTS_FIELD", "customfield_10016")

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
