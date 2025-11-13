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

# Story Points custom fields (varies by Jira instance)
# Common values: customfield_10016, customfield_10026
JIRA_STORY_POINTS_FIELD = os.getenv("JIRA_STORY_POINTS_FIELD", "customfield_10016")
JIRA_STORY_POINTS_ESTIMATE_FIELD = os.getenv("JIRA_STORY_POINTS_ESTIMATE_FIELD", "customfield_10026")

def get_auth():
    """Returns the authentication object for Jira API requests."""
    return (JIRA_USER_EMAIL, JIRA_API_TOKEN)

def get_story_points(issue_fields):
    """
    Extract story points with fallback logic.
    
    Priority:
    1. If both fields are null → return 0
    2. If both fields have values → return Story Points field (priority)
    3. If only one has a value → return that value
    
    Args:
        issue_fields: The 'fields' dictionary from a Jira issue
        
    Returns:
        float: Story points value (0 if both fields are null)
    """
    sp_field = issue_fields.get(JIRA_STORY_POINTS_FIELD)
    sp_estimate_field = issue_fields.get(JIRA_STORY_POINTS_ESTIMATE_FIELD)
    
    # Both null - return 0
    if sp_field is None and sp_estimate_field is None:
        return 0
    
    # Both not null - use Story Points (priority)
    if sp_field is not None and sp_estimate_field is not None:
        return float(sp_field) if sp_field else 0
    
    # One is not null - use that one
    value = sp_field if sp_field is not None else sp_estimate_field
    return float(value) if value else 0

def validate_config():
    """Validates that all required configuration is present."""
    if not JIRA_API_URL:
        raise ValueError("JIRA_API_URL is not set in environment variables")
    if not JIRA_API_TOKEN:
        raise ValueError("JIRA_API_TOKEN is not set in environment variables")
    if not JIRA_USER_EMAIL:
        raise ValueError("JIRA_USER_EMAIL is not set in environment variables")
