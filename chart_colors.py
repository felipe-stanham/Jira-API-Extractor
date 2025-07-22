"""Chart color configuration for consistent styling across all charts."""

# Color configuration for issue types
ISSUE_TYPE_COLORS = {
    'Refinement': '4472C4',      # Blue
    'Story': '70AD47',           # Green  
    'Bug': 'E74C3C',             # Red
    'Emergency': 'FF0000',       # Bright Red
    'Ad-Hoc': 'F39C12',          # Orange
    'Support': '9B59B6'          # Purple
}

# Color configuration for statuses
STATUS_COLORS = {
    'To be Defined': 'BDC3C7',   # Light Gray
    'To Do': '85C1E9',           # Light Blue
    'In Progress': 'F7DC6F',     # Yellow
    'DEV': 'F8C471',             # Light Orange
    'QA': 'BB8FCE',              # Light Purple
    'Ready-For-Test': 'AED6F1',  # Pale Blue
    'Ready for PROD': '82E0AA',  # Light Green
    'PROD': '58D68D',            # Green
    'DONE': '28B463',            # Dark Green
    'Cancelled': 'EC7063'        # Light Red
}

# Default colors for items not in the configuration
DEFAULT_COLORS = [
    '2E86AB',  # Blue
    'A23B72',  # Purple
    'F18F01',  # Orange
    'C73E1D',  # Red
    '6A994E',  # Green
    '577590',  # Gray Blue
    'F2CC8F',  # Light Orange
    '81B29A',  # Sage Green
    'E07A5F',  # Coral
    '3D5A80'   # Dark Blue
]

def get_issue_type_color(issue_type):
    """Get color for a specific issue type."""
    return ISSUE_TYPE_COLORS.get(issue_type, None)

def get_status_color(status):
    """Get color for a specific status."""
    return STATUS_COLORS.get(status, None)

def get_default_color(index):
    """Get a default color by index (cycles through available colors)."""
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]

def assign_colors_to_series(items, color_map_func):
    """
    Assign colors to a list of items using the provided color mapping function.
    Falls back to default colors for unmapped items.
    
    Args:
        items: List of items (issue types, statuses, etc.)
        color_map_func: Function to get color for an item
        
    Returns:
        Dictionary mapping items to hex colors
    """
    color_assignments = {}
    default_index = 0
    
    for item in items:
        color = color_map_func(item)
        if color:
            color_assignments[item] = color
        else:
            color_assignments[item] = get_default_color(default_index)
            default_index += 1
    
    return color_assignments
