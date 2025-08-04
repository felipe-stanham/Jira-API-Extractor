# Jira API Extractor - GUI Application

A user-friendly Jira data extraction tool with a modern web interface. Extract issues, worklogs, and comments from Jira projects and export them to Excel with rich visualizations.

## Features

- **🖥️ Modern Web Interface**: Beautiful Streamlit-based GUI that runs in your browser
- **📦 Standalone Application**: No Python installation required - just double-click to run
- **⚙️ In-App Configuration**: Configure Jira credentials directly in the application
- **📊 Rich Data Extraction**: 
  - Extract all issues from specific sprints
  - Extract work logs within date ranges (project-wide)
  - Extract comments made within date ranges (project-wide)
- **📈 Advanced Excel Export**: Export to `.xlsx` with multiple sheets and charts:
  - Sprint Issues with full details
  - Work Logs with time tracking
  - Comments with timestamps
  - Charts with visual analytics
- **🎨 Visual Analytics**: Comprehensive charts in dedicated Charts sheet:
  - Issues by status (pie chart)
  - Issues by type (pie chart) 
  - Time by issue type per sprint (pie charts)
  - Time by issue type across sprints (stacked bar chart)
- **🔄 Real-time Progress**: Live progress updates during data extraction
- **💾 Persistent Settings**: Configuration saved automatically for future use

## 🚀 Quick Start (For End Users)

### Download & Run
1. **Download** the latest release: `JiraExtractor_macos_standalone.zip`
2. **Extract** the zip file
3. **Double-click** `JiraExtractorGUI_macos.app` to launch
4. **Configure** your Jira credentials in the sidebar (first time only)
5. **Extract** your data using the web interface!

### First-Time Setup
1. The app will open in your default web browser
2. In the sidebar, enter your Jira details:
   - **Jira URL**: `https://your-company.atlassian.net`
   - **Email**: Your Jira login email
   - **API Token**: [Get your token here](https://id.atlassian.com/manage-profile/security/api-tokens)
3. Click **"💾 Save Configuration"**
4. Your settings are saved to `JiraExtractor.env` for future use

## 🛠️ For Developers

### Project Structure
```
├── main.py                    # CLI entry point (for developers)
├── run_gui.py                 # GUI launcher
├── streamlit_app.py           # Streamlit web interface
├── config.py                  # Configuration management (uses JiraExtractor.env)
├── jira_api.py                # Jira API client with pagination
├── excel_exporter.py          # Excel export with charts
├── charts_helper_enhanced.py  # Chart creation functions
├── chart_colors.py            # Chart color schemes
├── utils.py                   # Utility functions
├── build_executables.py       # Build script for standalone app
├── requirements.txt           # Python dependencies
├── .env.example               # Template for JiraExtractor.env
└── README.md                  # This file
```

### Development Setup
1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Create** `JiraExtractor.env` based on `.env.example`
4. **Run** the GUI: `python3 run_gui.py`
5. **Or run** CLI: `python3 main.py --project YOUR_PROJECT --sprint SPRINT_ID`

## 📱 Using the GUI Application

### Main Interface
1. **Project Code**: Enter your Jira project key (e.g., "NG", "PROJ")
2. **Sprint IDs**: Enter sprint IDs separated by commas (e.g., "123,124,125")
3. **Date Range**: Use date pickers for worklog/comment extraction
4. **Quick Buttons**: 
   - Last 7 days
   - Last 30 days  
   - This month
   - Last month

### Extraction Options
- **Sprint + Date Range**: Get sprint issues AND worklogs/comments in date range
- **Sprint Only**: Get only sprint issues
- **Date Range Only**: Get only worklogs/comments in date range

### Real-time Progress
- Live progress bar during extraction
- Detailed logs showing current operation
- Automatic file download when complete

## 💻 CLI Usage (For Developers)

### Arguments
- `--project`: (Required) Jira project key (e.g., `NG`)
- `--sprint`: (Optional) Sprint ID(s), comma-separated
- `--start_date`: (Optional) Start date (`YYYY-MM-DD`)
- `--end_date`: (Optional) End date (`YYYY-MM-DD`)

### Examples
```bash
# Get sprint issues + worklogs in date range
python3 main.py --project NG --sprint 528 --start_date 2025-07-14 --end_date 2025-07-18

# Get only sprint issues
python3 main.py --project NG --sprint 528

# Get only worklogs/comments in date range
python3 main.py --project NG --start_date 2025-07-14 --end_date 2025-07-18
```

## 🏗️ Building Standalone Application

### For Developers: Creating Distribution
```bash
# Build the standalone .app bundle for macOS
python3 build_executables.py

# Output will be in dist/
# - JiraExtractorGUI_macos.app (the main app)
# - JiraExtractor_macos_standalone.zip (distribution package)
```

### Build Requirements
- Python 3.9+
- PyInstaller
- All project dependencies

### Distribution Package Contents
- `JiraExtractorGUI_macos.app` - The main application
- `JiraExtractor.env` - Configuration template
- `README.txt` - User instructions

## 🎯 Key Features

### 1. **Modern GUI Interface**
- Beautiful Streamlit web interface
- Real-time progress tracking
- In-app configuration management
- Automatic browser opening

### 2. **Comprehensive Data Extraction**
- Complete pagination support for large datasets
- Sprint issues with full details
- Project-wide worklogs and comments
- Flexible date range selection

### 3. **Advanced Excel Export**
- Multiple sheets with rich formatting
- Dynamic charts with professional styling
- Formula-based calculations
- Color-coded visualizations

### 4. **User-Friendly Configuration**
- No hidden files (uses `JiraExtractor.env`)
- In-app credential management
- Persistent settings across sessions
- Multiple apps can coexist in same folder

## 📊 Output

The application generates a comprehensive Excel file (`JiraExport.xlsx`) with up to 4 sheets:

### 1. **Sprint Issues Sheet**
- Complete issue details (key, summary, status, type, assignee, etc.)
- Sprint information and story points
- Links and priority information
- Formatted for easy reading

### 2. **Work Logs Sheet** 
- Time entries with author and date
- Issue keys and descriptions
- Sprint associations
- Time spent calculations

### 3. **Comments Sheet**
- All comments with timestamps
- Author information
- Issue context
- Formatted comment content

### 4. **Charts Sheet**
- **Issues by Status**: Pie chart showing distribution
- **Issues by Type**: Pie chart for issue types
- **Time by Type per Sprint**: Individual pie charts for each sprint
- **Time by Type (Stacked)**: Horizontal bar chart across all sprints
- **Summary Statistics**: Formula-based calculations

## 🔧 Configuration

### JiraExtractor.env File
The app uses `JiraExtractor.env` for configuration:
```env
JIRA_API_URL="https://your-company.atlassian.net"
JIRA_USER_EMAIL="your-email@company.com"
JIRA_API_TOKEN="your-api-token"
STREAMLIT_PORT=8501
```

### Getting Your API Token
1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "Jira Extractor")
4. Copy the token and paste it in the app

## 🚨 Troubleshooting

### Common Issues
- **App won't launch**: Make sure you're double-clicking the `.app` file, not the executable inside
- **Configuration won't save**: Check that you have write permissions in the app directory
- **No data extracted**: Verify your Jira credentials and project access
- **Charts not showing**: Ensure you have data in the corresponding sheets

### For Developers
- **SSL Warnings**: Suppress with `PYTHONWARNINGS="ignore:NotOpenSSLWarning"`
- **Port conflicts**: Change `STREAMLIT_PORT` in `JiraExtractor.env`
- **Build issues**: Ensure all dependencies are installed

---

**Jira API Extractor v2.0** - Built with ❤️ using Python, Streamlit, and PyInstaller
