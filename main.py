import warnings
from urllib3.exceptions import NotOpenSSLWarning
# Suppress the warning at the very top of the script to ensure it's active
# before any other modules (like requests) are imported.
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

import os
import requests
import argparse
from dotenv import load_dotenv
from datetime import datetime, timezone
from openpyxl import Workbook
from openpyxl.chart import PieChart, Reference
from collections import Counter

# Load environment variables from .env file
load_dotenv()

# Jira API credentials from environment variables
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")

def get_auth():
    """Returns the authentication object for Jira API requests."""
    return (JIRA_USER_EMAIL, JIRA_API_TOKEN)

def parse_adf_to_text(adf):
    """Parses an Atlassian Document Format object into a plain text string."""
    if not isinstance(adf, dict) or 'content' not in adf:
        # If it's not a valid ADF object, return it as is (might be a simple string).
        return str(adf)

    text_content = []
    for block in adf.get('content', []):
        if block.get('type') == 'paragraph':
            for item in block.get('content', []):
                if item.get('type') == 'text':
                    text_content.append(item.get('text', ''))
    return " ".join(text_content)

def get_issues_in_sprint(project_key, sprint_id):
    """Fetches all issues in a given sprint using the Agile API."""
    agile_url = f"{JIRA_API_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    headers = {"Accept": "application/json"}
    params = {'jql': f'project = "{project_key}"', 'fields': 'summary,status,parent,issuetype', 'maxResults': 100}
    try:
        response = requests.get(agile_url, headers=headers, params=params, auth=get_auth())
        response.raise_for_status()
        return response.json().get('issues', [])
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_work_logs(project_key, start_date, end_date):
    """Fetches all work log entries within a date range for a project."""
    search_url = f"{JIRA_API_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    jql = f'project = "{project_key}" AND worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
    params = {'jql': jql, 'fields': 'worklog,summary,issuetype,status', 'maxResults': 1000}
    try:
        response = requests.get(search_url, headers=headers, params=params, auth=get_auth())
        response.raise_for_status()
        issues_with_worklogs = response.json().get('issues', [])
        all_worklogs = []
        for issue in issues_with_worklogs:
            issue_worklogs = issue.get('fields', {}).get('worklog', {}).get('worklogs', [])
            for worklog in issue_worklogs:
                worklog_started_str = worklog.get('started')
                if worklog_started_str[-3] != ':':
                    worklog_started_str = worklog_started_str[:-2] + ':' + worklog_started_str[-2:]
                worklog_date = datetime.fromisoformat(worklog_started_str).astimezone(timezone.utc)
                start_date_aware = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                end_date_aware = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if start_date_aware <= worklog_date <= end_date_aware:
                    comment_obj = worklog.get('comment', {})
                    comment_text = parse_adf_to_text(comment_obj)
                    all_worklogs.append({
                        'issueKey': issue.get('key'),
                        'summary': issue.get('fields', {}).get('summary'),
                        'issueType': issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                        'status': issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                        'author': worklog.get('author', {}).get('displayName'),
                        'timeSpent': worklog.get('timeSpent'),
                        'timeSpentHours': round(worklog.get('timeSpentSeconds', 0) / 3600, 2),
                        'startedDate': worklog_date.strftime('%Y-%m-%d'),
                        'comment': comment_text
                    })
        return all_worklogs
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_comments_in_date_range(project_key, start_date, end_date):
    """Fetches all comments created within a date range for a project."""
    search_url = f"{JIRA_API_URL}/rest/api/3/search"
    headers = {"Accept": "application/json"}
    jql = f'project = "{project_key}" AND updatedDate >= "{start_date}" AND updatedDate <= "{end_date}"'
    params = {'jql': jql, 'fields': 'comment,summary,status,parent,issuetype', 'maxResults': 1000}
    try:
        response = requests.get(search_url, headers=headers, params=params, auth=get_auth())
        response.raise_for_status()
        issues = response.json().get('issues', [])
        all_comments = []
        for issue in issues:
            comments_in_issue = issue.get('fields', {}).get('comment', {}).get('comments', [])
            for comment in comments_in_issue:
                comment_created_str = comment.get('created')
                if comment_created_str[-3] != ':':
                    comment_created_str = comment_created_str[:-2] + ':' + comment_created_str[-2:]
                comment_date = datetime.fromisoformat(comment_created_str).astimezone(timezone.utc)
                start_date_aware = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                end_date_aware = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if start_date_aware <= comment_date <= end_date_aware:
                    comment_body = parse_adf_to_text(comment.get('body', ''))
                    all_comments.append({
                        'issueKey': issue.get('key'),
                        'summary': issue.get('fields', {}).get('summary'),
                        'status': issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                        'parent_summary': issue.get('fields', {}).get('parent', {}).get('fields', {}).get('summary', 'N/A'),
                        'issueType': issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                        'comment_date': comment_date.strftime('%Y-%m-%d'),
                        'comment_author': comment.get('author', {}).get('displayName'),
                        'comment_body': comment_body
                    })
        return all_comments
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def save_to_excel(issues, worklogs, comments):
    """Saves the fetched data to an Excel file, including a pie chart for issue status."""
    wb = Workbook()
    wb.remove(wb.active) # Remove the default sheet

    if issues:
        ws_issues = wb.create_sheet(title="Sprint Issues")
        ws_issues.append(['Key', 'Type', 'Summary', 'Status', 'Parent Summary'])
        for issue in issues:
            fields = issue.get('fields', {})
            parent_summary = fields.get('parent', {}).get('fields', {}).get('summary', 'N/A')
            issue_type = fields.get('issuetype', {}).get('name', 'N/A')
            ws_issues.append([issue.get('key'), issue_type, fields.get('summary'), fields.get('status', {}).get('name'), parent_summary])

        # --- Create Pie Chart for Issue Status ---
        if issues:
            status_counts = Counter(issue.get('fields', {}).get('status', {}).get('name', 'N/A') for issue in issues)
            
            # Create a summary table for the chart data in columns G and H
            ws_issues['G1'] = 'Status'
            ws_issues['H1'] = 'Count'
            
            for row, (status, count) in enumerate(status_counts.items(), start=2):
                ws_issues.cell(row=row, column=7, value=status)
                ws_issues.cell(row=row, column=8, value=count)

            pie = PieChart()
            labels = Reference(ws_issues, min_col=7, min_row=2, max_row=len(status_counts) + 1)
            data = Reference(ws_issues, min_col=8, min_row=1, max_row=len(status_counts) + 1)
            pie.add_data(data, titles_from_data=True)
            pie.set_categories(labels)
            pie.title = "Issues by Status"

            # Add the chart to the sheet
            ws_issues.add_chart(pie, "I2")

    if worklogs:
        ws_worklogs = wb.create_sheet(title="Work Logs")
        ws_worklogs.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Author', 'Time Spent', 'Time Spent (Hours)', 'Date', 'Comment'])
        for log in worklogs:
            ws_worklogs.append([log['issueKey'], log['issueType'], log['summary'], log['status'], log['author'], log['timeSpent'], log['timeSpentHours'], log['startedDate'], log['comment']])

    if comments:
        ws_comments = wb.create_sheet(title="Comments")
        ws_comments.append(['Issue Key', 'Summary', 'Status', 'Parent Summary', 'Issue Type', 'Comment Date', 'Comment Author', 'Comment'])
        for comment in comments:
            ws_comments.append([comment['issueKey'], comment['summary'], comment['status'], comment['parent_summary'], comment['issueType'], comment['comment_date'], comment['comment_author'], comment['comment_body']])

    if not wb.sheetnames:
        return False, None, "No data was fetched to save."

    try:
        filename = "JiraExport.xlsx"
        wb.save(filename)
        return True, filename, None
    except Exception as e:
        return False, None, str(e)

def main():
    """Main function to parse arguments and run the export process."""
    parser = argparse.ArgumentParser(description='Jira Sprint and Work Log Exporter.')
    parser.add_argument('--project', required=True, help='Jira Project Key (e.g., NG).')
    parser.add_argument('--sprint', help='Jira Sprint ID (optional).')
    parser.add_argument('--start_date', help='Start date for work logs and comments (YYYY-MM-DD, optional).')
    parser.add_argument('--end_date', help='End date for work logs and comments (YYYY-MM-DD, optional).')

    args = parser.parse_args()

    # Validate that if one date is provided, both are.
    if (args.start_date and not args.end_date) or (not args.start_date and args.end_date):
        print("Error: Both --start_date and --end_date must be provided together.")
        return

    issues = None
    if args.sprint:
        print(f"Fetching issues for sprint {args.sprint} in project {args.project}...")
        issues = get_issues_in_sprint(args.project.upper(), args.sprint)
        if isinstance(issues, dict) and 'error' in issues:
            print(f"Error fetching issues: {issues['error']}")
            return

    worklogs = None
    comments = None
    if args.start_date and args.end_date:
        print(f"Fetching work logs from {args.start_date} to {args.end_date}...")
        worklogs = get_work_logs(args.project.upper(), args.start_date, args.end_date)
        if isinstance(worklogs, dict) and 'error' in worklogs:
            print(f"Error fetching work logs: {worklogs['error']}")
            return

        print(f"Fetching comments from {args.start_date} to {args.end_date}...")
        comments = get_comments_in_date_range(args.project.upper(), args.start_date, args.end_date)
        if isinstance(comments, dict) and 'error' in comments:
            print(f"Error fetching comments: {comments['error']}")
            return

    print("Saving data to Excel...")
    success, filename, error = save_to_excel(issues, worklogs, comments)
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
    else:
        print(f"Error saving to Excel: {error}")

if __name__ == '__main__':
    main()
