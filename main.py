"""
Jira API Extractor - Main application module.

This script extracts data from Jira using the Atlassian API and exports it to Excel.
It supports extracting sprint issues, worklogs, and comments with improved pagination
and modular architecture.
"""

import warnings
from urllib3.exceptions import NotOpenSSLWarning
# Suppress the warning at the very top of the script to ensure it's active
# before any other modules (like requests) are imported.
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

import os
import argparse
from datetime import datetime

from config import validate_config
from jira_api import JiraAPIClient
from excel_exporter import ExcelExporter

def validate_date_format(date_string):
    """Validates date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def main():
    """Main function to parse arguments and run the export process."""
    parser = argparse.ArgumentParser(description='Jira Sprint and Work Log Exporter.')
    parser.add_argument('--project', required=True, help='Jira Project Key (e.g., NG).')
    parser.add_argument('--sprint', help='Jira Sprint ID(s) (optional). Use comma-separated values for multiple sprints (e.g., 528,560).')
    parser.add_argument('--start_date', help='Start date for work logs and comments (YYYY-MM-DD, optional).')
    parser.add_argument('--end_date', help='End date for work logs and comments (YYYY-MM-DD, optional).')
    parser.add_argument('--epic_label', help='Epic label to filter epics by (optional). Exports all issues from epics with this label.')
    parser.add_argument('--jql', help='Additional JQL filter (optional). Applies to sprint and epic issues only, not comments/worklogs.')

    args = parser.parse_args()

    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        return

    # Validate that if one date is provided, both are.
    if (args.start_date and not args.end_date) or (not args.start_date and args.end_date):
        print("Error: Both --start_date and --end_date must be provided together.")
        return

    # Validate date formats
    if args.start_date and not validate_date_format(args.start_date):
        print("Error: start_date must be in YYYY-MM-DD format.")
        return
    
    if args.end_date and not validate_date_format(args.end_date):
        print("Error: end_date must be in YYYY-MM-DD format.")
        return

    # Validate date range
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        if start_date > end_date:
            print("Error: start_date must be before or equal to end_date.")
            return

    # Initialize API client and exporter
    jira_client = JiraAPIClient()
    exporter = ExcelExporter()

    # Fetch data based on provided arguments
    issues = None
    issues_by_sprint = {}  # Dictionary to store issues by sprint ID
    worklogs = None
    comments = None
    epic_label_issues = None
    open_epic_issues = None

    if args.sprint:
        # Parse comma-separated sprint IDs
        sprint_ids = [sprint.strip() for sprint in args.sprint.split(',')]
        
        for sprint_id in sprint_ids:
            print(f"Fetching issues for sprint {sprint_id} in project {args.project}...")
            sprint_issues = jira_client.get_issues_in_sprint(args.project.upper(), sprint_id, jql=args.jql)
            if isinstance(sprint_issues, dict) and 'error' in sprint_issues:
                print(f"Error fetching issues for sprint {sprint_id}: {sprint_issues['error']}")
                continue
            
            # Get sprint details for the name
            sprint_details = jira_client.get_sprint_details(sprint_id)
            sprint_name = sprint_details.get('name', f'Sprint {sprint_id}') if sprint_details else f'Sprint {sprint_id}'
            
            # Add sprint information to each issue
            for issue in sprint_issues:
                issue['sprint_id'] = sprint_id
                issue['sprint_name'] = sprint_name
            
            issues_by_sprint[sprint_id] = {
                'issues': sprint_issues,
                'name': sprint_name
            }
            print(f"Found {len(sprint_issues)} issues in sprint {sprint_id} ({sprint_name})")
        
        # Combine all issues for backward compatibility
        issues = []
        for sprint_data in issues_by_sprint.values():
            issues.extend(sprint_data['issues'])

    if args.start_date and args.end_date:
        print(f"Fetching work logs from {args.start_date} to {args.end_date}...")
        worklogs = jira_client.get_all_worklogs_in_date_range(args.project.upper(), args.start_date, args.end_date)
        if isinstance(worklogs, dict) and 'error' in worklogs:
            print(f"Error fetching work logs: {worklogs['error']}")
            return
        print(f"Found {len(worklogs)} work logs")

        print(f"Fetching comments from {args.start_date} to {args.end_date}...")
        comments = jira_client.get_comments_in_date_range(args.project.upper(), args.start_date, args.end_date)
        if isinstance(comments, dict) and 'error' in comments:
            print(f"Error fetching comments: {comments['error']}")
            return
        print(f"Found {len(comments)} comments")
    
    # Fetch epic-based data
    if args.epic_label:
        print(f"Fetching epics with label '{args.epic_label}'...")
        epics = jira_client.get_epics_by_label(args.project.upper(), args.epic_label)
        if epics:
            print(f"Found {len(epics)} epics with label '{args.epic_label}'")
            all_epic_issues = []
            epic_statuses = {}
            
            for epic in epics:
                epic_key = epic.get('key')
                epic_status = epic.get('fields', {}).get('status', {}).get('name', 'N/A')
                epic_statuses[epic_key] = epic_status
                
                print(f"  Fetching issues for epic {epic_key}...")
                epic_issues = jira_client.get_issues_in_epic(epic_key, jql=args.jql)
                print(f"  Found {len(epic_issues)} issues in epic {epic_key}")
                all_epic_issues.extend(epic_issues)
            
            epic_label_issues = {
                'issues': all_epic_issues,
                'epic_statuses': epic_statuses
            }
            print(f"Total: {len(all_epic_issues)} issues from epics with label '{args.epic_label}'")
        else:
            print(f"Warning: No epics found with label '{args.epic_label}'")
            epic_label_issues = {'issues': [], 'epic_statuses': {}}
    
    # Always fetch open epics
    print(f"Fetching open epics in project {args.project}...")
    open_epics = jira_client.get_open_epics(args.project.upper())
    if open_epics:
        print(f"Found {len(open_epics)} open epics")
        all_open_epic_issues = []
        open_epic_statuses = {}
        
        for epic in open_epics:
            epic_key = epic.get('key')
            epic_status = epic.get('fields', {}).get('status', {}).get('name', 'N/A')
            open_epic_statuses[epic_key] = epic_status
            
            print(f"  Fetching issues for epic {epic_key}...")
            epic_issues = jira_client.get_issues_in_epic(epic_key, jql=args.jql)
            print(f"  Found {len(epic_issues)} issues in epic {epic_key}")
            all_open_epic_issues.extend(epic_issues)
        
        open_epic_issues = {
            'issues': all_open_epic_issues,
            'epic_statuses': open_epic_statuses
        }
        print(f"Total: {len(all_open_epic_issues)} issues from open epics")
    else:
        print("No open epics found")
        open_epic_issues = {'issues': [], 'epic_statuses': {}}

    # Check if any data was fetched
    if not any([issues, worklogs, comments, epic_label_issues, open_epic_issues]):
        print("No data to export. Please provide either --sprint, --epic_label, or both --start_date and --end_date.")
        return

    print("Saving data to Excel...")
    success, filename, error = exporter.save_to_excel(
        issues, worklogs, comments, 
        issues_by_sprint=issues_by_sprint,
        epic_label_issues=epic_label_issues,
        open_epic_issues=open_epic_issues
    )
    
    if success:
        summary = []
        if issues is not None:
            summary.append(f"{len(issues)} issues")
        if worklogs is not None:
            summary.append(f"{len(worklogs)} work logs")
        if comments is not None:
            summary.append(f"{len(comments)} comments")
        
        print(f"\nExport complete! Found {', '.join(summary)}.")
        print(f"Data saved to {os.path.abspath(filename)}")
        
        # List the sheets created
        wb = exporter.get_workbook()
        if wb:
            print(f"Excel file contains {len(wb.sheetnames)} sheets: {', '.join(wb.sheetnames)}")
    else:
        print(f"Error saving to Excel: {error}")

if __name__ == '__main__':
    main()
