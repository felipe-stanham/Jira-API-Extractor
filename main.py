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
    parser.add_argument('--sprint', help='Jira Sprint ID (optional).')
    parser.add_argument('--start_date', help='Start date for work logs and comments (YYYY-MM-DD, optional).')
    parser.add_argument('--end_date', help='End date for work logs and comments (YYYY-MM-DD, optional).')

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
    worklogs = None
    comments = None

    if args.sprint:
        print(f"Fetching issues for sprint {args.sprint} in project {args.project}...")
        issues = jira_client.get_issues_in_sprint(args.project.upper(), args.sprint)
        if isinstance(issues, dict) and 'error' in issues:
            print(f"Error fetching issues: {issues['error']}")
            return
        print(f"Found {len(issues)} issues in sprint {args.sprint}")

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

    # Check if any data was fetched
    if not any([issues, worklogs, comments]):
        print("No data to export. Please provide either --sprint or both --start_date and --end_date.")
        return

    print("Saving data to Excel...")
    success, filename, error = exporter.save_to_excel(issues, worklogs, comments)
    
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
