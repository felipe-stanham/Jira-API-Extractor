"""Excel export functionality for Jira data."""

from openpyxl import Workbook
from openpyxl.chart import PieChart, BarChart, Reference
from openpyxl.chart.label import DataLabelList
from collections import Counter
from charts_helper_clean import create_clean_charts_sheet

class ExcelExporter:
    """Handles Excel export functionality."""
    
    def __init__(self):
        self.wb = None
    
    def save_to_excel(self, issues, worklogs, comments, filename="JiraExport.xlsx"):
        """Saves the fetched data to an Excel file with separate sheets and charts."""
        self.wb = Workbook()
        
        # Remove default sheet
        if "Sheet" in self.wb.sheetnames:
            self.wb.remove(self.wb["Sheet"])
        
        sheets_created = []
        
        # Create Sprint Issues sheet
        if issues:
            ws_issues = self.wb.create_sheet(title="Sprint Issues")
            ws_issues.append(['Issue Key', 'Issue Type', 'Summary', 'Status', 'Parent Summary'])
            
            for issue in issues:
                parent_summary = 'N/A'
                parent_field = issue.get('fields', {}).get('parent')
                if parent_field:
                    parent_summary = parent_field.get('fields', {}).get('summary', 'N/A')
                
                ws_issues.append([
                    issue.get('key'),
                    issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                    issue.get('fields', {}).get('summary'),
                    issue.get('fields', {}).get('status', {}).get('name', 'N/A'),
                    parent_summary
                ])
            
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
        
        # Create Charts sheet if we have issues data
        if issues:
            self._create_charts_sheet(issues, worklogs)
            sheets_created.append("Charts")
        
        if not sheets_created:
            return False, None, "No data was fetched to save."
        
        try:
            self.wb.save(filename)
            return True, filename, None
        except Exception as e:
            return False, None, str(e)
    
    def _create_charts_sheet(self, issues, worklogs=None):
        """Creates a separate sheet for charts using the clean charts helper."""
        create_clean_charts_sheet(self.wb, issues, worklogs)
    
    def get_workbook(self):
        """Returns the current workbook instance."""
        return self.wb
