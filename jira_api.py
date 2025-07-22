"""Jira API client module for data extraction."""

import requests
from datetime import datetime, timezone
from config import JIRA_API_URL, get_auth
from utils import parse_adf_to_text, paginate_request

class JiraAPIClient:
    """Client for interacting with Jira API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = JIRA_API_URL
        self.auth = get_auth()
        self.headers = {"Accept": "application/json"}
    
    def get_issues_in_sprint(self, project_key, sprint_id):
        """Fetches all issues in a given sprint using the Agile API with pagination."""
        agile_url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        params = {
            'jql': f'project = "{project_key}"',
            'fields': 'summary,status,parent,issuetype'
        }
        
        try:
            issues = paginate_request(
                self.session, agile_url, self.headers, params, self.auth
            )
            return issues
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_sprint_details(self, sprint_id):
        """
        Fetches sprint details including name.
        """
        sprint_url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}"
        
        try:
            response = self.session.get(
                sprint_url,
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch sprint details for sprint {sprint_id}: {str(e)}")
            return None
    
    def get_all_worklogs_in_date_range(self, project_key, start_date, end_date):
        """
        Fetches all worklogs within a date range for a project using the worklog search API.
        This is more efficient than fetching all issues and filtering locally.
        """
        # Use the worklog search endpoint for better performance
        worklog_search_url = f"{self.base_url}/rest/api/3/worklog/updated"
        
        # Convert dates to timestamps (milliseconds since epoch)
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59).timestamp() * 1000)
        
        params = {
            'since': start_timestamp,
            'expand': 'properties'
        }
        
        try:
            # Get all worklog IDs updated in the time range
            worklog_ids = paginate_request(
                self.session, worklog_search_url, self.headers, params, self.auth,
                max_results_key='maxResults', start_at_key='startAt'
            )
            
            if not worklog_ids:
                return []
            
            # Extract worklog IDs from the response
            ids = []
            for item in worklog_ids:
                if 'worklogId' in item:
                    ids.append(item['worklogId'])
                elif 'values' in item:
                    ids.extend([wl['worklogId'] for wl in item['values']])
            
            if not ids:
                return []
            
            # Fetch detailed worklog information in batches
            all_worklogs = []
            batch_size = 1000  # Jira API limit
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                worklog_details_url = f"{self.base_url}/rest/api/3/worklog/list"
                
                payload = {
                    "ids": batch_ids,
                    "expand": ["properties"]
                }
                
                response = self.session.post(
                    worklog_details_url,
                    json=payload,
                    headers={**self.headers, "Content-Type": "application/json"},
                    auth=self.auth
                )
                response.raise_for_status()
                
                worklogs_batch = response.json()
                
                # Filter worklogs by project and date range
                for worklog in worklogs_batch:
                    # Get issue details to check project
                    issue_key = worklog.get('issueId')
                    if issue_key:
                        issue_url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
                        issue_response = self.session.get(
                            issue_url,
                            headers=self.headers,
                            params={'fields': 'project,summary,issuetype,status,sprint'},
                            auth=self.auth
                        )
                        
                        if issue_response.status_code == 200:
                            issue_data = issue_response.json()
                            issue_project = issue_data.get('fields', {}).get('project', {}).get('key', '')
                            
                            if issue_project.upper() == project_key.upper():
                                # Check if worklog is within date range
                                worklog_started_str = worklog.get('started')
                                if worklog_started_str:
                                    # Fix timezone format if needed
                                    if worklog_started_str[-3] != ':':
                                        worklog_started_str = worklog_started_str[:-2] + ':' + worklog_started_str[-2:]
                                    
                                    # Parse the worklog date and keep it in its original timezone
                                    worklog_datetime = datetime.fromisoformat(worklog_started_str)
                                    
                                    # Convert to date only for comparison
                                    worklog_date = worklog_datetime.date()
                                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                                    
                                    if start_date_obj <= worklog_date <= end_date_obj:
                                        comment_obj = worklog.get('comment', {})
                                        comment_text = parse_adf_to_text(comment_obj)
                                        
                                        # Extract sprint information
                                        sprint_info = 'N/A'
                                        sprint_field = issue_data.get('fields', {}).get('sprint')
                                        if sprint_field:
                                            if isinstance(sprint_field, list) and sprint_field:
                                                # Take the last (most recent) sprint
                                                sprint = sprint_field[-1]
                                                if isinstance(sprint, dict):
                                                    sprint_name = sprint.get('name', 'N/A')
                                                    sprint_id = sprint.get('id', 'N/A')
                                                    sprint_info = f"{sprint_name} (ID: {sprint_id})"
                                                else:
                                                    sprint_info = str(sprint)
                                            elif isinstance(sprint_field, dict):
                                                sprint_name = sprint_field.get('name', 'N/A')
                                                sprint_id = sprint_field.get('id', 'N/A')
                                                sprint_info = f"{sprint_name} (ID: {sprint_id})"
                                        
                                        all_worklogs.append({
                                            'issueKey': issue_data.get('key'),
                                            'summary': issue_data.get('fields', {}).get('summary'),
                                            'issueType': issue_data.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                                            'status': issue_data.get('fields', {}).get('status', {}).get('name', 'N/A'),
                                            'author': worklog.get('author', {}).get('displayName', 'Unknown'),
                                            'timeSpent': worklog.get('timeSpent', '0m'),
                                            'timeSpentHours': round(worklog.get('timeSpentSeconds', 0) / 3600, 2),
                                            'startedDate': worklog_date.strftime('%Y-%m-%d'),  # Date only, no time
                                            'sprint': sprint_info,
                                            'comment': comment_text
                                        })
            
            return all_worklogs
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching worklogs: {str(e)}")
            # Fallback to the original method
            return self._get_worklogs_fallback(project_key, start_date, end_date)
    
    def _get_worklogs_fallback(self, project_key, start_date, end_date):
        """Fallback method using the original approach with pagination."""
        search_url = f"{self.base_url}/rest/api/3/search"
        jql = f'project = "{project_key}" AND worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
        params = {
            'jql': jql,
            'fields': 'worklog,summary,issuetype,status,sprint'
        }
        
        try:
            issues_with_worklogs = paginate_request(
                self.session, search_url, self.headers, params, self.auth
            )
            
            all_worklogs = []
            for issue in issues_with_worklogs:
                issue_worklogs = issue.get('fields', {}).get('worklog', {}).get('worklogs', [])
                for worklog in issue_worklogs:
                    worklog_started_str = worklog.get('started')
                    if worklog_started_str[-3] != ':':
                        worklog_started_str = worklog_started_str[:-2] + ':' + worklog_started_str[-2:]
                    
                    # Parse the worklog date and keep it in its original timezone
                    worklog_datetime = datetime.fromisoformat(worklog_started_str)
                    
                    # Convert to date only for comparison
                    worklog_date = worklog_datetime.date()
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    
                    if start_date_obj <= worklog_date <= end_date_obj:
                        comment_obj = worklog.get('comment', {})
                        comment_text = parse_adf_to_text(comment_obj)
                        
                        # Extract sprint information
                        sprint_info = 'N/A'
                        sprint_field = issue.get('fields', {}).get('sprint')
                        if sprint_field:
                            if isinstance(sprint_field, list) and sprint_field:
                                # Take the last (most recent) sprint
                                sprint = sprint_field[-1]
                                if isinstance(sprint, dict):
                                    sprint_name = sprint.get('name', 'N/A')
                                    sprint_id = sprint.get('id', 'N/A')
                                    sprint_info = f"{sprint_name} (ID: {sprint_id})"
                                else:
                                    sprint_info = str(sprint)
                            elif isinstance(sprint_field, dict):
                                sprint_name = sprint_field.get('name', 'N/A')
                                sprint_id = sprint_field.get('id', 'N/A')
                                sprint_info = f"{sprint_name} (ID: {sprint_id})"
                        
                        all_worklogs.append({
                            'issueKey': issue.get('key'),
                            'summary': issue.get('fields', {}).get('summary'),
                            'issueType': issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                            'status': issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                            'author': worklog.get('author', {}).get('displayName', 'Unknown'),
                            'timeSpent': worklog.get('timeSpent', '0m'),
                            'timeSpentHours': round(worklog.get('timeSpentSeconds', 0) / 3600, 2),
                            'startedDate': worklog_date.strftime('%Y-%m-%d'),  # Date only, no time
                            'sprint': sprint_info,
                            'comment': comment_text
                        })
            
            return all_worklogs
            
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_comments_in_date_range(self, project_key, start_date, end_date):
        """Fetches all comments created within a date range for a project with pagination."""
        search_url = f"{self.base_url}/rest/api/3/search"
        # Fix JQL syntax for comment date filtering
        jql = f'project = "{project_key}" AND updated >= "{start_date}" AND updated <= "{end_date}"'
        params = {
            'jql': jql,
            'fields': 'summary,status,parent,issuetype,comment',
            'expand': 'changelog'
        }
        
        try:
            issues_with_comments = paginate_request(
                self.session, search_url, self.headers, params, self.auth
            )
            
            all_comments = []
            for issue in issues_with_comments:
                comments = issue.get('fields', {}).get('comment', {}).get('comments', [])
                for comment in comments:
                    comment_created_str = comment.get('created')
                    if comment_created_str:
                        if comment_created_str[-3] != ':':
                            comment_created_str = comment_created_str[:-2] + ':' + comment_created_str[-2:]
                        comment_date = datetime.fromisoformat(comment_created_str).astimezone(timezone.utc)
                        start_date_aware = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                        end_date_aware = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                        
                        if start_date_aware <= comment_date <= end_date_aware:
                            comment_body_obj = comment.get('body', {})
                            comment_body = parse_adf_to_text(comment_body_obj)
                            
                            parent_summary = 'N/A'
                            parent_field = issue.get('fields', {}).get('parent')
                            if parent_field:
                                parent_summary = parent_field.get('fields', {}).get('summary', 'N/A')
                            
                            all_comments.append({
                                'issueKey': issue.get('key'),
                                'summary': issue.get('fields', {}).get('summary'),
                                'status': issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                                'parent_summary': parent_summary,
                                'issueType': issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                                'comment_date': comment_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'comment_author': comment.get('author', {}).get('displayName', 'Unknown'),
                                'comment_body': comment_body
                            })
            
            return all_comments
            
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
