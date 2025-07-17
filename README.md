# Jira API Extractor

This is a simple terminal application to extract information from Jira and export it to an Excel file.

## Features

- Extract all issues from a specific sprint.
- Extract all work logs within a specified date range.
- Extract all comments made within a specified date range.
- Conditionally fetch data based on provided arguments (sprint, dates, or both).
- Export the fetched data into a single `.xlsx` file with separate sheets for "Sprint Issues", "Work Logs", and "Comments".

## Setup

1.  Clone the repository.
2.  Install the dependencies: `pip install -r requirements.txt`
3.  Create a `.env` file based on the `.env.example` and fill in your Jira details (URL, email, and API token).

## Usage

The script is run from the command line and accepts several arguments to control what data is extracted.

### Arguments

-   `--project`: (Required) The key for your Jira project (e.g., `NG`).
-   `--sprint`: (Optional) The ID of the sprint you want to extract issues from.
-   `--start_date`: (Optional) The start date for extracting work logs and comments (`YYYY-MM-DD`).
-   `--end_date`: (Optional) The end date for extracting work logs and comments (`YYYY-MM-DD`).

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

### Suppressing Warnings

If you see a `NotOpenSSLWarning`, you can safely suppress it by prefixing the command with `PYTHONWARNINGS="ignore:NotOpenSSLWarning"`:

```bash
PYTHONWARNINGS="ignore:NotOpenSSLWarning" python3 main.py --project NG --sprint 528
```
