# Jira API Extractor - GUI Application

A user-friendly Jira data extraction tool with a modern web interface. Extract issues, worklogs, and comments from Jira projects and export them to Excel with rich visualizations.

## Features

- **🖥️ Modern Web Interface**: Beautiful Streamlit-based GUI that runs in your browser
- **⚙️ In-App Configuration**: Configure Jira credentials directly in the application
- **📊 Rich Data Extraction**: 
  - Extract all issues from specific sprints
  - Extract work logs within date ranges (project-wide)
  - Extract comments made within date ranges (project-wide)
  - **NEW**: Filter epics by label and extract all related issues
  - **NEW**: Automatically extract all open epic work
- **📈 Advanced Excel Export**: Export to `.xlsx` with multiple sheets and charts:
  - Sprint Issues with **story points, parent key, and status category**
  - Work Logs with time tracking
  - Comments with timestamps
  - **NEW**: Epics with Label sheet (conditional)
  - **NEW**: Open Epics sheet (always included)
  - Charts with visual analytics
  - **NEW**: Progress sheet with 7 progress visualization charts
  - **NEW**: Time Tracking sheet with formatted tables for easy pivot analysis
- **🎨 Visual Analytics**: Comprehensive charts in dedicated Charts sheet:
  - Issues by status (pie chart)
  - Issues by type (pie chart) 
  - Time by issue type per sprint (pie charts)
  - Time by issue type across sprints (stacked bar chart)
- **🔄 Real-time Progress**: Live progress updates during data extraction
- **💾 Persistent Settings**: Configuration saved automatically for future use

## 🚀 Quick Start

### Project Structure
```
├── main.py                    # CLI entry point
├── run_gui.py                 # GUI launcher script
├── streamlit_app.py           # Streamlit web interface
├── config.py                  # Configuration management (uses JiraExtractor.env)
├── jira_api.py                # Jira API client with pagination
├── excel_exporter.py          # Excel export with charts
├── charts_helper_enhanced.py  # Chart creation functions
├── progress_charts_helper.py  # Progress chart creation functions
├── progress_data_aggregator.py # Progress data aggregation
├── chart_colors.py            # Chart color schemes
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── .env.example               # Template for JiraExtractor.env
└── README.md                  # This file
```

### Setup
1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Create** `JiraExtractor.env` based on `.env.example`
4. **Run** the GUI: `python3 run_gui.py` (or `streamlit run streamlit_app.py`)
5. **Or run** CLI: `python3 main.py --project YOUR_PROJECT --sprint SPRINT_ID`

## 📱 Using the GUI Application

### Main Interface
1. **Project Code**: Enter your Jira project key (e.g., "NG", "PROJ")
2. **Sprint IDs**: Enter sprint IDs separated by commas (e.g., "123,124,125")
3. **Epic Label**: (Optional) Filter epics by label to extract all related issues
4. **Date Range**: Use date pickers for worklog/comment extraction
5. **Quick Buttons**: 
   - Last 7 days
   - Last 30 days  
   - This month
   - Last month

### Extraction Options
- **Sprint + Date Range**: Get sprint issues AND worklogs/comments in date range
- **Sprint Only**: Get only sprint issues with enhanced columns
- **Date Range Only**: Get only worklogs/comments in date range
- **Epic Label**: Get all issues from epics with specific label
- **Combined**: Mix any combination of the above options

### Real-time Progress
- Live progress bar during extraction
- Detailed logs showing current operation
- Automatic file download when complete

## 💻 CLI Usage (For Developers)

### Arguments
- `--project`: (Required) Jira project key (e.g., `NG`)
- `--sprint`: (Optional) Sprint ID(s), comma-separated
- `--epic_label`: (Optional) Epic label to filter by (e.g., `Q1-2025`)
- `--start_date`: (Optional) Start date (`YYYY-MM-DD`)
- `--end_date`: (Optional) End date (`YYYY-MM-DD`)

### Examples
```bash
# Get sprint issues with enhanced columns (story points, parent key, status category)
python3 main.py --project NG --sprint 528

# Get sprint issues + worklogs in date range
python3 main.py --project NG --sprint 528 --start_date 2025-07-14 --end_date 2025-07-18

# Get only worklogs/comments in date range
python3 main.py --project NG --start_date 2025-07-14 --end_date 2025-07-18

# Get all issues from epics with specific label
python3 main.py --project NG --epic_label "Q1-2025"

# Combined: Sprint + Epic Label + Date Range
python3 main.py --project NG --sprint 528 --epic_label "Q1-2025" --start_date 2025-07-14 --end_date 2025-07-18
```

## 🎯 Key Features

### 1. **Modern GUI Interface**
- Beautiful Streamlit web interface
- Real-time progress tracking
- In-app configuration management
- Automatic browser opening

### 2. **Comprehensive Data Extraction**
- Complete pagination support for large datasets
- Sprint issues with **story points, parent key, and status category**
- Project-wide worklogs and comments
- **Epic-based filtering** by label
- **Automatic open epic tracking**
- Flexible date range selection

### 3. **Advanced Excel Export**
- Multiple sheets with rich formatting
- **Up to 9 sheets**: Sprint(s), Epics with Label, Open Epics, Work Logs, Comments, Charts, Progress, Time Tracking
- Dynamic charts with professional styling
- Formula-based calculations
- Color-coded visualizations
- **7 progress charts** showing epic completion by percentage and story points
- **3 time tracking tables** for easy pivot table creation and analysis

### 4. **User-Friendly Configuration**
- No hidden files (uses `JiraExtractor.env`)
- In-app credential management
- Persistent settings across sessions

## 📊 Output

The application generates a comprehensive Excel file (`JiraExport.xlsx`) with up to 9 sheets:

### 1. **Sprint Issues Sheet(s)** ⭐ ENHANCED
- Complete issue details (key, summary, status, type)
- **NEW**: Story points estimate
- **NEW**: Parent key (direct epic reference)
- **NEW**: Status category (To Do, In Progress, Done)
- Sprint information
- Parent summary
- One sheet per sprint (for multiple sprints)

### 2. **Epics with Label Sheet** ⭐ NEW (Conditional)
- All issues from epics matching specified label
- Same columns as Sprint sheets plus **Epic Status**
- Ignores date ranges - shows all work for labeled epics
- Only created when `--epic_label` parameter provided
- Useful for tracking quarterly or initiative-based work

### 3. **Open Epics Sheet** ⭐ NEW (Always Included)
- All issues from epics not in "Done" status
- Same columns as Sprint sheets plus **Epic Status**
- Provides visibility into current commitments
- Always created - shows all active epic work
- Useful for understanding current workload

### 4. **Work Logs Sheet** 
- Time entries with author and date
- Issue keys and descriptions
- Sprint associations
- Time spent calculations

### 5. **Comments Sheet**
- All comments with timestamps
- Author information
- Issue context
- Formatted comment content

### 6. **Charts Sheet**
- **Issues by Status**: Pie chart showing distribution
- **Issues by Type**: Pie chart for issue types
- **Time by Type per Sprint**: Individual pie charts for each sprint
- **Time by Type (Stacked)**: Horizontal bar chart across all sprints
- **Summary Statistics**: Formula-based calculations

### 7. **Progress Sheet** ⭐ NEW
- **Sprint Progress Charts** (3 charts per sprint):
  - Progress by Epic (%) - Horizontal bar chart showing completion percentage
  - Progress by Epic (Story Points) - Stacked bar chart (Done/In Progress/To Do)
  - Composition by Epic - Pie chart showing epic distribution
- **Epic Label Progress Charts** (2 charts, conditional on `--epic_label`):
  - Progress by Epic (%) - Completion percentage for labeled epics
  - Progress by Epic (Story Points) - Stacked breakdown for labeled epics
- **Open Epic Progress Charts** (2 charts, always included):
  - Progress by Epic (%) - Completion percentage for all open epics
  - Progress by Epic (Story Points) - Stacked breakdown for all open epics
- **Features**:
  - Epics sorted by completion percentage (highest first)
  - Excludes epics with 0 story points
  - Truncates long epic names (40 chars + "...")
  - Handles "No Epic" group for orphaned issues
  - Color-coded: Done (green), In Progress (yellow), To Do (blue)

### 8. **Time Tracking Sheet** ⭐ NEW
- **Detailed Time Tracking Table**:
  - Columns: Date, Author, Issue Key, Hours
  - Sorted by date, then author, then issue
  - Granular view of all time entries
  - Excel Table: DetailedTimeTracking
- **Summary by Author and Date Table**:
  - Columns: Author, Date, Total Hours
  - Daily time tracking per developer
  - Sorted by author, then date
  - Excel Table: SummaryByAuthorDate
- **Total Hours by Author Table**:
  - Columns: Author, Total Hours
  - Overall time summary per developer
  - Sorted by author
  - Excel Table: TotalByAuthor
- **Features**:
  - Professional formatted Excel tables
  - Easy conversion to pivot tables (Insert > PivotTable in Excel)
  - Multiple aggregation levels for different analysis needs
  - Only created when worklogs exist
  - Includes user-friendly instructions

## 🔧 Configuration

### JiraExtractor.env File
The app uses `JiraExtractor.env` for configuration:
```env
JIRA_API_URL="https://your-company.atlassian.net"
JIRA_USER_EMAIL="your-email@company.com"
JIRA_API_TOKEN="your-api-token"
STREAMLIT_PORT=8501

# Optional: Story Points custom field (varies by Jira instance)
# Common values: customfield_10016, customfield_10026
# JIRA_STORY_POINTS_FIELD="customfield_10016"
```

### Story Points Configuration
The story points field varies by Jira instance. The default is `customfield_10016`. If your instance uses a different field:
1. Find your story points field ID in Jira
2. Add `JIRA_STORY_POINTS_FIELD="customfield_XXXXX"` to your `JiraExtractor.env`
3. Restart the application

### Getting Your API Token
1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "Jira Extractor")
4. Copy the token and paste it in the app

## 🚨 Troubleshooting

### Common Issues
- **Configuration won't save**: Check that you have write permissions in the directory
- **No data extracted**: Verify your Jira credentials and project access
- **Charts not showing**: Ensure you have data in the corresponding sheets
- **SSL Warnings**: Suppress with `PYTHONWARNINGS="ignore:NotOpenSSLWarning"`
- **Port conflicts**: Change `STREAMLIT_PORT` in `JiraExtractor.env`

---

**Jira API Extractor v2.0** - Built with ❤️ using Python and Streamlit
