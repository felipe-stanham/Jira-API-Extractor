#!/usr/bin/env python3
"""
Progress Data Aggregator Module

Provides data aggregation functions for progress charts.
Groups issues by epic, calculates story points by status category,
and prepares data for chart generation.
"""

from config import JIRA_STORY_POINTS_FIELD


def truncate_epic_name(name, max_length=40):
    """
    Truncates epic name to specified length with ellipsis.
    
    Args:
        name: Epic name to truncate
        max_length: Maximum length (default 40)
        
    Returns:
        Truncated name with "..." if longer than max_length
    """
    if not name or len(name) <= max_length:
        return name
    return name[:max_length] + "..."


def calculate_epic_progress(issues):
    """
    Calculates progress data for each epic from a list of issues.
    
    Args:
        issues: List of issue dictionaries from Jira API
        
    Returns:
        List of dicts with epic progress data, sorted by completion % (highest first).
        Each dict contains:
        - epic_key: Parent epic key (or "No Epic")
        - epic_name: Truncated epic name
        - done_points: Story points with status category "Done"
        - in_progress_points: Story points with status category "In Progress"
        - to_do_points: Story points with status category "To Do"
        - total_points: Sum of all story points
        - percentage: Completion percentage (done / total * 100)
    """
    epic_data = {}
    
    for issue in issues:
        # Get parent epic info
        parent_field = issue.get('fields', {}).get('parent')
        if parent_field:
            epic_key = parent_field.get('key', 'No Epic')
            epic_name = parent_field.get('fields', {}).get('summary', epic_key)
        else:
            epic_key = 'No Epic'
            epic_name = 'No Epic'
        
        # Initialize epic entry if not exists
        if epic_key not in epic_data:
            epic_data[epic_key] = {
                'epic_key': epic_key,
                'epic_name': truncate_epic_name(epic_name),
                'done_points': 0,
                'in_progress_points': 0,
                'to_do_points': 0,
                'total_points': 0
            }
        
        # Get story points
        story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD)
        if story_points is None:
            story_points = 0
        
        # Get status category
        status_category = issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name', '')
        
        # Aggregate by status category
        if status_category == 'Done':
            epic_data[epic_key]['done_points'] += story_points
        elif status_category == 'In Progress':
            epic_data[epic_key]['in_progress_points'] += story_points
        else:  # To Do or other
            epic_data[epic_key]['to_do_points'] += story_points
        
        epic_data[epic_key]['total_points'] += story_points
    
    # Calculate percentages and filter out epics with 0 total points
    result = []
    for epic in epic_data.values():
        if epic['total_points'] > 0:  # Exclude epics with 0 story points
            epic['percentage'] = (epic['done_points'] / epic['total_points'] * 100) if epic['total_points'] > 0 else 0
            result.append(epic)
    
    # Sort by completion percentage (highest first)
    result.sort(key=lambda x: x['percentage'], reverse=True)
    
    return result


def aggregate_by_epic(issues):
    """
    Groups issues by parent epic key.
    
    Args:
        issues: List of issue dictionaries from Jira API
        
    Returns:
        Dict with epic keys as keys and lists of issues as values
    """
    epic_groups = {}
    
    for issue in issues:
        # Get parent epic key
        parent_field = issue.get('fields', {}).get('parent')
        if parent_field:
            epic_key = parent_field.get('key', 'No Epic')
        else:
            epic_key = 'No Epic'
        
        if epic_key not in epic_groups:
            epic_groups[epic_key] = []
        
        epic_groups[epic_key].append(issue)
    
    return epic_groups


def calculate_sprint_composition(issues):
    """
    Calculates sprint composition data for pie chart.
    Shows total story points per epic (all statuses).
    
    Args:
        issues: List of issue dictionaries from Jira API
        
    Returns:
        List of dicts with composition data, each containing:
        - epic_key: Parent epic key (or "No Epic")
        - epic_name: Truncated epic name
        - total_points: Total story points for this epic
        - percentage: Percentage of sprint total
    """
    epic_totals = {}
    sprint_total = 0
    
    for issue in issues:
        # Get parent epic info
        parent_field = issue.get('fields', {}).get('parent')
        if parent_field:
            epic_key = parent_field.get('key', 'No Epic')
            epic_name = parent_field.get('fields', {}).get('summary', epic_key)
        else:
            epic_key = 'No Epic'
            epic_name = 'No Epic'
        
        # Initialize epic entry if not exists
        if epic_key not in epic_totals:
            epic_totals[epic_key] = {
                'epic_key': epic_key,
                'epic_name': truncate_epic_name(epic_name),
                'total_points': 0
            }
        
        # Get story points
        story_points = issue.get('fields', {}).get(JIRA_STORY_POINTS_FIELD)
        if story_points is None:
            story_points = 0
        
        epic_totals[epic_key]['total_points'] += story_points
        sprint_total += story_points
    
    # Calculate percentages and filter out epics with 0 total points
    result = []
    for epic in epic_totals.values():
        if epic['total_points'] > 0:  # Exclude epics with 0 story points
            epic['percentage'] = (epic['total_points'] / sprint_total * 100) if sprint_total > 0 else 0
            result.append(epic)
    
    return result


def filter_issues_by_sheet(all_issues, sheet_type):
    """
    Filters issues based on sheet type.
    This is a placeholder for future filtering logic if needed.
    
    Args:
        all_issues: Dict containing all issue lists
        sheet_type: Type of sheet ('sprint', 'epic_label', 'open_epic')
        
    Returns:
        Filtered list of issues
    """
    if sheet_type == 'sprint':
        return all_issues.get('sprint_issues', [])
    elif sheet_type == 'epic_label':
        return all_issues.get('epic_label_issues', [])
    elif sheet_type == 'open_epic':
        return all_issues.get('open_epic_issues', [])
    else:
        return []
