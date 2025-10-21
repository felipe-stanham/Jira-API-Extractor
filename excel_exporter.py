"""Excel export functionality for Jira data."""

from openpyxl import Workbook
from openpyxl.chart import PieChart, BarChart, Reference
from openpyxl.chart.label import DataLabelList
from collections import Counter
from charts_helper_enhanced import create_clean_charts_sheet
from config import JIRA_STORY_POINTS_FIELD

class ExcelExporter:
    """Handles Excel export functionality."""
    
    def __init__(self):
        self.wb = None
    
    def save_to_excel(self, issues, worklogs, comments, filename="JiraExport.xlsx", issues_by_sprint=None, epic_label_issues=None, open_epic_issues=None):
        """Saves the fetched data to an Excel file with separate sheets and charts."""
        self.wb = Workbook()
        
        # Remove default sheet
        if "Sheet" in self.wb.sheetnames:
            self.wb.remove(self.wb["Sheet"])
        
        sheets_created = []
        
        # Create Sprint Issues sheets - one for each sprint if multiple sprints provided
        if issues_by_sprint:
            for sprint_id, sprint_data in issues_by_sprint.items():
                sprint_issues = sprint_data['issues']
                sprint_name = sprint_data['name']
                
                # Create sheet with sprint name (truncate if too long for Excel)
                sheet_title = f"Sprint {sprint_id}"
                if len(sheet_title) > 31:  # Excel sheet name limit
                    sheet_title = f"Sprint {sprint_id}"[:31]
                
                ws_issues = self.wb.create_sheet(title=sheet_title)
                ws_issues.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Sprint', 'Parent Summary', 'Story Points', 'Parent Key', 'Status Category'])
                
                for issue in sprint_issues:
                    parent_summary = 'N/A'
                    parent_key = 'N/A'
                    parent_field = issue.get('fields', {}).get('parent')
                    if parent_field:
                        parent_summary = parent_field.get('fields', {}).get('summary', 'N/A')
                        parent_key = parent_field.get('key', 'N/A')
                    
                    # Get story points
                    story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD, 'N/A')
                    if story_points is None:
                        story_points = 'N/A'
                    
                    # Get status category
                    status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'N/A')
                    
                    ws_issues.append([
                        issue.get('key'),
                        issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                        issue.get('fields', {}).get('summary'),
                        issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                        sprint_name,
                        parent_summary,
                        story_points,
                        parent_key,
                        status_category
                    ])
                
                sheets_created.append(sheet_title)
        elif issues:
            # Fallback for single sprint or backward compatibility
            ws_issues = self.wb.create_sheet(title="Sprint Issues")
            # Check if issues have sprint information
            has_sprint_info = any(issue.get('sprint_name') for issue in issues)
            
            if has_sprint_info:
                ws_issues.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Sprint', 'Parent Summary', 'Story Points', 'Parent Key', 'Status Category'])
            else:
                ws_issues.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Parent Summary', 'Story Points', 'Parent Key', 'Status Category'])
            
            for issue in issues:
                parent_summary = 'N/A'
                parent_key = 'N/A'
                parent_field = issue.get('fields', {}).get('parent')
                if parent_field:
                    parent_summary = parent_field.get('fields', {}).get('summary', 'N/A')
                    parent_key = parent_field.get('key', 'N/A')
                
                # Get story points
                story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD, 'N/A')
                if story_points is None:
                    story_points = 'N/A'
                
                # Get status category
                status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'N/A')
                
                row_data = [
                    issue.get('key'),
                    issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                    issue.get('fields', {}).get('summary'),
                    issue.get('fields', {}).get('status', {}).get('name', 'N/A')
                ]
                
                if has_sprint_info:
                    row_data.append(issue.get('sprint_name', 'N/A'))
                
                row_data.extend([parent_summary, story_points, parent_key, status_category])
                ws_issues.append(row_data)
            
            sheets_created.append("Sprint Issues")
        
        # Create Work Logs sheet
        if worklogs:
            ws_worklogs = self.wb.create_sheet(title="Work Logs")
            ws_worklogs.append([
                'Issue Key', 'Issue Type', 'Summary', 'Status', 
                'Author', 'Time Spent', 'Time Spent (Hours)', 'Date', 'Sprint', 'Comment'
            ])
            
            for log in worklogs:
                ws_worklogs.append([
                    log['issueKey'], log['issueType'], log['summary'], log['status'],
                    log['author'], log['timeSpent'], log['timeSpentHours'], 
                    log['startedDate'], log['sprint'], log['comment']
                ])
            
            sheets_created.append("Work Logs")
        
        # Create Comments sheet
        if comments:
            ws_comments = self.wb.create_sheet(title="Comments")
            ws_comments.append([
                'Issue Key', 'Summary', 'Status', 'Parent Summary', 
                'Issue Type', 'Comment Date', 'Comment Author', 'Comment'
            ])
            
            for comment in comments:
                ws_comments.append([
                    comment['issueKey'], comment['summary'], comment['status'],
                    comment['parent_summary'], comment['issueType'], comment['comment_date'],
                    comment['comment_author'], comment['comment_body']
                ])
            
            sheets_created.append("Comments")
        
        # Create Epics with Label sheet (conditional - only if epic_label_issues provided)
        if epic_label_issues:
            self._write_epic_sheet(epic_label_issues, "Epics with Label")
            sheets_created.append("Epics with Label")
        
        # Create Open Epics sheet (always created if open_epic_issues provided)
        if open_epic_issues:
            self._write_epic_sheet(open_epic_issues, "Open Epics")
            sheets_created.append("Open Epics")
        
        # Create Charts sheet if we have issues data
        if issues:
            self._create_charts_sheet(issues, worklogs, issues_by_sprint)
            sheets_created.append("Charts")
        
        if not sheets_created:
            return False, None, "No data was fetched to save."
        
        try:
            self.wb.save(filename)
            return True, filename, None
        except Exception as e:
            return False, None, str(e)
    
    def _create_charts_sheet(self, issues, worklogs=None, issues_by_sprint=None):
        """Creates a separate sheet for charts using the clean charts helper."""
        create_clean_charts_sheet(self.wb, issues, worklogs, issues_by_sprint)
    
    def _write_epic_sheet(self, epic_data, sheet_name):
        """
        Creates a sheet for epic-based issues (Epics with Label or Open Epics).
        
        Args:
            epic_data: Dictionary with 'issues' list and 'epic_statuses' dict
            sheet_name: Name of the sheet to create
        """
        ws = self.wb.create_sheet(title=sheet_name)
        ws.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Sprint', 'Parent Summary', 
                   'Story Points', 'Parent Key', 'Status Category', 'Epic Status'])
        
        issues = epic_data.get('issues', [])
        epic_statuses = epic_data.get('epic_statuses', {})
        
        for issue in issues:
            parent_summary = 'N/A'
            parent_key = 'N/A'
            epic_status = 'N/A'
            
            parent_field = issue.get('fields', {}).get('parent')
            if parent_field:
                parent_summary = parent_field.get('fields', {}).get('summary', 'N/A')
                parent_key = parent_field.get('key', 'N/A')
                # Get epic status from the epic_statuses dict
                epic_status = epic_statuses.get(parent_key, 'N/A')
            
            # Get story points
            story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD, 'N/A')
            if story_points is None:
                story_points = 'N/A'
            
            # Get status category
            status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'N/A')
            
            # Get sprint info if available
            sprint_name = issue.get('sprint_name', 'N/A')
            
            ws.append([
                issue.get('key'),
                issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                issue.get('fields', {}).get('summary'),
                issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                sprint_name,
                parent_summary,
                story_points,
                parent_key,
                status_category,
                epic_status
            ])
    
    def get_workbook(self):
        """Returns the current workbook instance."""
        return self.wb
