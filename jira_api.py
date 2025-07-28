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
    
    def get_issue_sprints(self, issue_key):
        """
        Get all sprints for a given issue key.
        Returns a list of sprint information dictionaries.
        """
        try:
            # Get issue details with all fields to find sprint information
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            params = {
                'fields': '*all'  # Get all fields to find the sprint field
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code != 200:
                return []
            
            issue_data = response.json()
            fields = issue_data.get('fields', {})
            
            # Search for sprint information in all custom fields
            sprint_field = None
            
            # Common sprint field IDs to check
            possible_sprint_fields = [
                'customfield_10020', 'customfield_10001', 'customfield_10002', 
                'customfield_10003', 'customfield_10004', 'customfield_10005',
                'customfield_10006', 'customfield_10007', 'customfield_10008',
                'customfield_10009', 'customfield_10010', 'customfield_10011',
                'customfield_10012', 'customfield_10013', 'customfield_10014',
                'customfield_10015', 'customfield_10016', 'customfield_10017',
                'customfield_10018', 'customfield_10019', 'customfield_10021',
                'customfield_10022', 'customfield_10023', 'customfield_10024',
                'customfield_10025'
            ]
            
            # Check each possible sprint field
            for field_id in possible_sprint_fields:
                field_value = fields.get(field_id)
                if field_value:
                    # Check if this looks like sprint data
                    if isinstance(field_value, list) and len(field_value) > 0:
                        # Check if first item looks like sprint data
                        first_item = field_value[0]
                        if (isinstance(first_item, dict) and 'id' in first_item) or \
                           (isinstance(first_item, str) and ('id=' in first_item or 'name=' in first_item)):
                            sprint_field = field_value
                            break
                    elif isinstance(field_value, dict) and 'id' in field_value:
                        sprint_field = [field_value]
                        break
                    elif isinstance(field_value, str) and ('id=' in field_value or 'name=' in field_value):
                        sprint_field = [field_value]
                        break
            
            if not sprint_field:
                return []
            
            # Parse sprint information
            sprint_info_list = []
            for sprint_data in sprint_field:
                if sprint_data:
                    sprint_info = {}
                    
                    # Extract sprint information from the sprint object
                    if hasattr(sprint_data, 'id'):
                        # If it's a sprint object
                        sprint_info['id'] = sprint_data.id
                        sprint_info['name'] = getattr(sprint_data, 'name', 'Unknown')
                        sprint_info['state'] = getattr(sprint_data, 'state', 'Unknown')
                    elif isinstance(sprint_data, dict):
                        # If it's a dictionary
                        sprint_info['id'] = sprint_data.get('id', 'Unknown')
                        sprint_info['name'] = sprint_data.get('name', 'Unknown')
                        sprint_info['state'] = sprint_data.get('state', 'Unknown')
                    else:
                        # If it's a string (sometimes sprint data comes as string)
                        sprint_str = str(sprint_data)
                        
                        # Try to parse sprint ID and name from string
                        import re
                        id_match = re.search(r'id=(\d+)', sprint_str)
                        name_match = re.search(r'name=([^,\]]+)', sprint_str)
                        state_match = re.search(r'state=([^,\]]+)', sprint_str)
                        
                        sprint_info['id'] = id_match.group(1) if id_match else 'Unknown'
                        sprint_info['name'] = name_match.group(1) if name_match else 'Unknown'
                        sprint_info['state'] = state_match.group(1) if state_match else 'Unknown'
                    
                    if sprint_info.get('id') != 'Unknown':
                        sprint_info_list.append(sprint_info)
            
            return sprint_info_list
            
        except Exception as e:
            print(f"Warning: Could not fetch sprint information for issue {issue_key}: {str(e)}")
            return []
    
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
            all_worklogs_raw = []
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
                all_worklogs_raw.extend(worklogs_batch)
            
            # Step 1: Filter worklogs by date range and collect unique issue IDs
            filtered_worklogs = []
            unique_issue_ids = set()
            
            for worklog in all_worklogs_raw:
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
                        issue_id = worklog.get('issueId')
                        if issue_id:
                            filtered_worklogs.append((worklog, worklog_date))
                            unique_issue_ids.add(issue_id)
            
            if not filtered_worklogs:
                return []
            
            # Step 2: Fetch issue details for unique issues (batch processing)
            print(f"Fetching details for {len(unique_issue_ids)} unique issues...")
            issue_details_cache = {}
            issue_sprint_cache = {}
            
            for issue_id in unique_issue_ids:
                # Get basic issue details
                issue_url = f"{self.base_url}/rest/api/3/issue/{issue_id}"
                issue_response = self.session.get(
                    issue_url,
                    headers=self.headers,
                    params={'fields': 'project,summary,issuetype,status,key'},
                    auth=self.auth
                )
                
                if issue_response.status_code == 200:
                    issue_data = issue_response.json()
                    issue_project = issue_data.get('fields', {}).get('project', {}).get('key', '')
                    
                    # Only process issues from the target project
                    if issue_project.upper() == project_key.upper():
                        issue_key = issue_data.get('key')
                        issue_details_cache[issue_id] = issue_data
                        
                        # Get comprehensive sprint information for this issue
                        if issue_key:
                            sprint_info_list = self.get_issue_sprints(issue_key)
                            if sprint_info_list:
                                # Format sprint information for display
                                sprint_names = []
                                for sprint in sprint_info_list:
                                    sprint_name = sprint.get('name', 'Unknown')
                                    sprint_id = sprint.get('id', 'Unknown')
                                    sprint_state = sprint.get('state', 'Unknown')
                                    sprint_names.append(f"{sprint_name} (ID: {sprint_id}, {sprint_state})")
                                issue_sprint_cache[issue_id] = "; ".join(sprint_names)
                            else:
                                issue_sprint_cache[issue_id] = 'N/A'
            
            # Step 3: Build final worklog list with cached issue and sprint information
            all_worklogs = []
            
            for worklog, worklog_date in filtered_worklogs:
                issue_id = worklog.get('issueId')
                if issue_id in issue_details_cache:
                    issue_data = issue_details_cache[issue_id]
                    sprint_info = issue_sprint_cache.get(issue_id, 'N/A')
                    
                    comment_obj = worklog.get('comment', {})
                    comment_text = parse_adf_to_text(comment_obj)
                    
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
        """Fallback method using the original approach with pagination and comprehensive sprint fetching."""
        search_url = f"{self.base_url}/rest/api/3/search"
        jql = f'project = "{project_key}" AND worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
        params = {
            'jql': jql,
            'fields': 'worklog,summary,issuetype,status,key'
        }
        
        try:
            issues_with_worklogs = paginate_request(
                self.session, search_url, self.headers, params, self.auth
            )
            
            # Step 1: Collect all issues and their worklogs within date range
            filtered_worklogs = []
            unique_issue_keys = set()
            
            for issue in issues_with_worklogs:
                issue_key = issue.get('key')
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
                        filtered_worklogs.append((issue, worklog, worklog_date))
                        if issue_key:
                            unique_issue_keys.add(issue_key)
            
            if not filtered_worklogs:
                return []
            
            # Step 2: Get comprehensive sprint information for each unique issue
            print(f"Fetching sprint details for {len(unique_issue_keys)} unique issues (fallback method)...")
            issue_sprint_cache = {}
            
            for issue_key in unique_issue_keys:
                sprint_info_list = self.get_issue_sprints(issue_key)
                if sprint_info_list:
                    # Format sprint information for display
                    sprint_names = []
                    for sprint in sprint_info_list:
                        sprint_name = sprint.get('name', 'Unknown')
                        sprint_id = sprint.get('id', 'Unknown')
                        sprint_state = sprint.get('state', 'Unknown')
                        sprint_names.append(f"{sprint_name} (ID: {sprint_id}, {sprint_state})")
                    issue_sprint_cache[issue_key] = "; ".join(sprint_names)
                else:
                    issue_sprint_cache[issue_key] = 'N/A'
            
            # Step 3: Build final worklog list with comprehensive sprint information
            all_worklogs = []
            
            for issue, worklog, worklog_date in filtered_worklogs:
                issue_key = issue.get('key')
                sprint_info = issue_sprint_cache.get(issue_key, 'N/A')
                
                comment_obj = worklog.get('comment', {})
                comment_text = parse_adf_to_text(comment_obj)
                
                all_worklogs.append({
                    'issueKey': issue_key,
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
