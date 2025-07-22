# Jira API Extractor

This is a modular terminal application to extract information from Jira and export it to an Excel file with improved performance and organization.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for API, configuration, utilities, and Excel export
- **Comprehensive Pagination**: Handles large datasets by automatically paginating through all results
- **Efficient Data Extraction**: 
  - Extract all issues from a specific sprint
  - Extract all work logs within a specified date range (project-wide, not limited to sprint)
  - Extract all comments made within a specified date range (project-wide, not limited to sprint)
- **Flexible Input Handling**: Conditionally fetch data based on provided arguments (sprint, dates, or both)
- **Enhanced Excel Export**: Export data into a single `.xlsx` file with separate sheets for "Sprint Issues", "Work Logs", "Comments", and "Charts"
- **Visual Analytics**: Multiple charts in dedicated Charts sheet:
  - Pie chart for issue status distribution
  - Pie chart for issues by type
  - Pie chart for total time by issue type
  - Bar chart for time spent by author and issue type
- **Formula-Based Analytics**: All chart data uses Excel formulas for dynamic updates
- **Robust Validation**: Input validation for dates, configuration, and data integrity

## Project Structure

```
├── main.py              # Main application entry point
├── config.py            # Configuration and authentication management
├── jira_api.py          # Jira API client with pagination support
├── excel_exporter.py    # Excel export functionality with charts
├── charts_helper.py     # Enhanced chart creation functions
├── utils.py             # Utility functions (ADF parsing, pagination)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Setup

1. Clone the repository.
2. Install the dependencies: `pip install -r requirements.txt`
3. Create a `.env` file based on the `.env.example` and fill in your Jira details (URL, email, and API token).

## Usage

The script is run from the command line and accepts several arguments to control what data is extracted.

### Arguments

- `--project`: (Required) The key for your Jira project (e.g., `NG`).
- `--sprint`: (Optional) The ID of the sprint you want to extract issues from.
- `--start_date`: (Optional) The start date for extracting work logs and comments (`YYYY-MM-DD`).
- `--end_date`: (Optional) The end date for extracting work logs and comments (`YYYY-MM-DD`).

**Note:** `--start_date` and `--end_date` must be used together.

### Examples

**1. Get all data (Sprint Issues, Work Logs, and Comments):**

```bash
python3 main.py --project NG --sprint 528 --start_date 2025-07-14 --end_date 2025-07-18
```

**2. Get only Sprint Issues:**

```bash
python3 main.py --project NG --sprint 528
```

**3. Get only Work Logs and Comments for a date range:**

```bash
python3 main.py --project NG --start_date 2025-07-14 --end_date 2025-07-18
```

## Improvements in This Version

### 1. **Complete Pagination Support**
- No data loss even in large projects with thousands of issues/worklogs/comments
- Automatic handling of Jira API pagination limits

### 2. **Efficient Worklog Extraction**
- Uses Jira's worklog search API for better performance
- Fetches all worklogs in date range regardless of sprint association
- Fallback mechanism for compatibility

### 3. **Modular Architecture**
- `config.py`: Centralized configuration management
- `jira_api.py`: API client with improved error handling
- `excel_exporter.py`: Dedicated Excel export with chart generation
- `utils.py`: Reusable utility functions

### 4. **Enhanced Charts**
- **Multiple chart types**: Pie charts for status/type distribution, bar charts for time analysis
- **Formula-based calculations**: All chart data uses Excel formulas for dynamic updates
- **Comprehensive analytics**: Issues by status, issues by type, time by type, time by author
- **Professional layout**: Charts positioned in dedicated sheet with proper spacing

### 5. **Improved Validation**
- Configuration validation on startup
- Date format validation
- Date range validation
- Better error messages

## Output

The script generates an Excel file (`JiraExport.xlsx`) with up to 4 sheets:

1. **Sprint Issues**: List of issues in the specified sprint
2. **Work Logs**: All worklogs in the date range for the project
3. **Comments**: All comments in the date range for the project  
4. **Charts**: Visual analytics including:
   - Pie chart for issues by status
   - Pie chart for issues by type  
   - Pie chart for total time by issue type
   - Bar chart for time spent by author and issue type
   - Summary statistics with formula-based calculations

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid configuration
- API authentication failures
- Network connectivity issues
- Invalid date formats or ranges
- Empty result sets

## Performance Notes

- Uses efficient API endpoints where possible
- Implements proper pagination to handle large datasets
- Includes fallback mechanisms for API compatibility
- Optimized for minimal API calls while ensuring complete data retrieval

If you see a `NotOpenSSLWarning`, you can safely suppress it by prefixing the command with `PYTHONWARNINGS="ignore:NotOpenSSLWarning"`:

```bash
PYTHONWARNINGS="ignore:NotOpenSSLWarning" python3 main.py --project NG --sprint 528
```
