"""Excel export functionality for Jira data."""

from openpyxl import Workbook
from openpyxl.chart import PieChart, BarChart, Reference
from openpyxl.chart.label import DataLabelList
from collections import Counter
from charts_helper_enhanced import create_clean_charts_sheet
from config import JIRA_STORY_POINTS_FIELD
from progress_data_aggregator import calculate_epic_progress, calculate_sprint_composition
from progress_charts_helper import create_percentage_bar_chart, create_stacked_bar_chart, create_composition_pie_chart

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
                    
                    # Get story points (use 0 if not set)
                    story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD)
                    if story_points is None:
                        story_points = 0
                    
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
                
                # Get story points (use 0 if not set)
                story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD)
                if story_points is None:
                    story_points = 0
                
                # Get status category
                status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'N/A')
                
                row_data = [
                    issue.get('key'),
                    issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A'),
                    issue.get('fields', {}).get('summary'),
                    issue.get('fields', {}).get('status', {}).get('name', 'N/A')
                ]
                
                if has_sprint_info:
                    row_data.append(issue.get('sprint_name', ''))
                
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
        
        # Create Progress sheet with progress charts
        if issues_by_sprint or epic_label_issues or open_epic_issues:
            progress_sheet = self._create_progress_sheet(issues_by_sprint, epic_label_issues, open_epic_issues)
            sheets_created.append(progress_sheet)
        
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
            
            # Get story points (use 0 if not set)
            story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD)
            if story_points is None:
                story_points = 0
            
            # Get status category
            status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', 'N/A')
            
            # Get sprint info if available (empty string if no sprint)
            sprint_name = issue.get('sprint_name', '')
            
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
    
    def _create_progress_sheet(self, issues_by_sprint=None, epic_label_issues=None, open_epic_issues=None):
        """
        Creates Progress sheet with progress visualization charts.
        
        Args:
            issues_by_sprint: Dict of sprint issues (sprint_id -> {name, issues})
            epic_label_issues: List of issues from "Epics with Label" sheet
            open_epic_issues: List of issues from "Open Epics" sheet
        """
        ws = self.wb.create_sheet(title="Progress")
        
        # Add sheet title
        ws['A1'] = "Progress Charts"
        ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)
        
        current_row = 3
        current_col = 1
        
        # Sprint Progress Charts (3 charts per sprint)
        if issues_by_sprint:
            for sprint_id, sprint_data in issues_by_sprint.items():
                sprint_issues = sprint_data['issues']
                sprint_name = sprint_data['name']
                
                # Calculate epic progress for this sprint
                epic_progress = calculate_epic_progress(sprint_issues)
                
                if epic_progress:  # Only create charts if there's data
                    # Chart 1: Sprint Progress in Percentage (Column A-B)
                    chart1, end_row1 = create_percentage_bar_chart(
                        ws, epic_progress, current_row,
                        f"{sprint_name} - Progress by Epic (%)"
                    )
                    ws.add_chart(chart1, f"A{current_row}")
                    
                    # Chart 2: Sprint Progress in Story Points (Stacked) (Column D-G)
                    chart2, end_row2 = create_stacked_bar_chart(
                        ws, epic_progress, current_row, 4,  # Start at column 4 (D)
                        f"{sprint_name} - Progress by Epic (Story Points)"
                    )
                    ws.add_chart(chart2, f"Q{current_row}")  # Column Q (17)
                    
                    # Chart 3: Sprint Composition (Pie) (Column I-J)
                    composition_data = calculate_sprint_composition(sprint_issues)
                    if composition_data:
                        chart3, end_row3 = create_composition_pie_chart(
                            ws, composition_data, current_row, 9,  # Start at column 9 (I)
                            f"{sprint_name} - Composition by Epic"
                        )
                        ws.add_chart(chart3, f"AG{current_row}")  # Column AG (33)
                    
                    # Move to next chart group
                    current_row = max(end_row1, end_row2, end_row3 if composition_data else end_row2) + 20
        
        # Epic Label Progress Charts (2 charts, conditional)
        if epic_label_issues and epic_label_issues.get('issues'):
            epic_progress = calculate_epic_progress(epic_label_issues['issues'])
            
            if epic_progress:
                # Chart 4: Epic Label Progress in Percentage (Column A-B)
                chart4, end_row4 = create_percentage_bar_chart(
                    ws, epic_progress, current_row,
                    "Epic Label Progress by Epic (%)"
                )
                ws.add_chart(chart4, f"A{current_row}")
                
                # Chart 5: Epic Label Progress in Story Points (Stacked) (Column D-G)
                chart5, end_row5 = create_stacked_bar_chart(
                    ws, epic_progress, current_row, 4,  # Start at column 4 (D)
                    "Epic Label Progress by Epic (Story Points)"
                )
                ws.add_chart(chart5, f"Q{current_row}")  # Column Q (17)
                
                # Move to next chart group
                current_row = max(end_row4, end_row5) + 20
        
        # Open Epic Progress Charts (2 charts, always created)
        if open_epic_issues and open_epic_issues.get('issues'):
            epic_progress = calculate_epic_progress(open_epic_issues['issues'])
            
            if epic_progress:
                # Chart 6: Open Epic Progress in Percentage (Column A-B)
                chart6, end_row6 = create_percentage_bar_chart(
                    ws, epic_progress, current_row,
                    "Open Epics Progress by Epic (%)"
                )
                ws.add_chart(chart6, f"A{current_row}")
                
                # Chart 7: Open Epic Progress in Story Points (Stacked) (Column D-G)
                chart7, end_row7 = create_stacked_bar_chart(
                    ws, epic_progress, current_row, 4,  # Start at column 4 (D)
                    "Open Epics Progress by Epic (Story Points)"
                )
                ws.add_chart(chart7, f"Q{current_row}")  # Column Q (17)
        
        return "Progress"
    
    def get_workbook(self):
        """Returns the current workbook instance."""
        return self.wb
