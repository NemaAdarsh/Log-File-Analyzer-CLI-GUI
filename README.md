# Log File Analyzer (CLI/GUI)

A comprehensive Python application for analyzing log files from web servers and applications. This tool provides both command-line interface (CLI) and graphical user interface (GUI) options for parsing, filtering, and summarizing log data.

## Features

- **Multi-format Support**: Parse various log formats including Apache/Nginx access logs, application logs, system logs, and IIS logs
- **Advanced Filtering**: Filter logs by date range, log level, keywords, and source components
- **Statistical Analysis**: Generate comprehensive statistics including error rates, hourly distributions, and source analysis
- **Export Capabilities**: Export filtered results to JSON, CSV, or TXT formats
- **Dual Interface**: Use either command-line interface for automation or GUI for interactive analysis
- **Real-time Processing**: Handle large log files efficiently with streaming parser
- **Professional Output**: Clean, formatted output suitable for reporting and documentation

## Requirements

- Python 3.6 or higher
- Standard library modules (no external dependencies required)
- tkinter (for GUI functionality, usually included with Python)

## Installation

1. Clone or download the project:
```bash
git clone <repository-url>
cd log-file-analyzer
```

2. Ensure Python 3.6+ is installed:
```bash
python --version
```

3. No additional installation required - uses only Python standard library

## Usage

### Command Line Interface (CLI)

#### Basic Usage
```bash
python log_analyzer.py <logfile>
```

#### Advanced Options
```bash
# Analyze specific log levels
python log_analyzer.py --file app.log --level ERROR WARNING

# Filter by date range
python log_analyzer.py --file server.log --start-date 2024-01-01 --end-date 2024-01-31

# Search for specific keywords
python log_analyzer.py --file app.log --keywords "timeout,connection,database"

# Filter by source component
python log_analyzer.py --file system.log --source "apache"

# Export results
python log_analyzer.py --file app.log --export results.json --format json

# Show only statistics
python log_analyzer.py --file app.log --stats-only
```

### Graphical User Interface (GUI)

Launch the GUI application:
```bash
python log_analyzer.py --gui
```

The GUI provides:
- File browser for log selection
- Interactive filter controls
- Real-time results display
- Export functionality
- Statistics overview

## Supported Log Formats

### Apache/Nginx Access Logs
```
192.168.1.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
```

### Application Logs
```
2024-01-15 14:30:25.123 [ERROR]: Database connection failed
2024-01-15 14:30:26,456 INFO: Application started successfully
```

### System Logs
```
Jan 15 14:30:25 server01 apache[1234]: Configuration reloaded
```

### IIS Logs
```
2024-01-15 14:30:25 192.168.1.1 GET /default.htm - 80 - 192.168.1.100 Mozilla/4.0 - 200 0 0 1234
```

## Command Line Arguments

| Argument | Short | Description | Example |
|----------|-------|-------------|---------|
| `file` | `-f` | Path to log file | `--file app.log` |
| `--start-date` | | Start date filter (YYYY-MM-DD) | `--start-date 2024-01-01` |
| `--end-date` | | End date filter (YYYY-MM-DD) | `--end-date 2024-01-31` |
| `--level` | `-l` | Log levels to include | `--level ERROR WARNING` |
| `--keywords` | `-k` | Keywords to search for | `--keywords "error,timeout"` |
| `--source` | `-s` | Filter by source component | `--source apache` |
| `--export` | `-e` | Export results to file | `--export results.json` |
| `--format` | | Export format (json/csv/txt) | `--format csv` |
| `--stats-only` | | Show only statistics | `--stats-only` |
| `--gui` | | Launch GUI interface | `--gui` |
| `--version` | | Show version information | `--version` |

## Output Formats

### JSON Export
```json
{
  "metadata": {
    "export_time": "2024-01-15T14:30:25.123456",
    "entry_count": 1500,
    "statistics": {...}
  },
  "entries": [
    {
      "timestamp": "2024-01-15T14:30:25.123456",
      "level": "ERROR",
      "message": "Database connection failed",
      "source": "webapp",
      "raw_line": "...",
      "line_number": 1234
    }
  ]
}
```

### CSV Export
```csv
Timestamp,Level,Source,Message,Line Number
2024-01-15T14:30:25.123456,ERROR,webapp,Database connection failed,1234
```

### Text Export
```
Log Analysis Report
Generated: 2024-01-15 14:30:25.123456
Total Entries: 1500

[2024-01-15 14:30:25] ERROR: Database connection failed
```

## Statistics Generated

The analyzer provides comprehensive statistics including:

- **Total entry count** and parsing success rate
- **Error and warning rates** as percentages
- **Log level distribution** with counts and percentages
- **Source component analysis** showing top contributors
- **Temporal analysis** including hourly distribution patterns
- **Date range coverage** of the analyzed logs
- **Top error and warning messages** for quick issue identification

## Examples

### Analyze Web Server Logs
```bash
python log_analyzer.py access.log --level ERROR --export errors.json
```

### Monitor Application Health
```bash
python log_analyzer.py --file app.log --start-date 2024-01-01 --keywords "error,exception,failed"
```

### Daily Report Generation
```bash
python log_analyzer.py --file system.log --stats-only --export daily_report.txt
```

### Interactive Analysis
```bash
python log_analyzer.py --gui
```

## Error Handling

The application includes comprehensive error handling for:

- **File not found** or permission denied scenarios
- **Invalid date formats** in command line arguments
- **Malformed log entries** with fallback parsing
- **Export failures** with detailed error messages
- **GUI exceptions** with user-friendly dialogs

## Performance Considerations

- **Memory efficient**: Streams large files without loading entirely into memory
- **Regex optimization**: Pre-compiled patterns for faster parsing
- **Batch processing**: Processes entries in chunks for better performance
- **GUI responsiveness**: Non-blocking operations with status updates

## Technical Architecture

### Core Components

1. **LogEntry**: Data structure representing parsed log entries
2. **LogParser**: Handles parsing of various log formats using regex patterns
3. **LogAnalyzer**: Main analysis engine with filtering and statistics generation
4. **LogAnalyzerGUI**: Tkinter-based graphical interface
5. **CLI Parser**: Command-line argument processing and execution

### Design Patterns

- **Strategy Pattern**: Multiple parsing strategies for different log formats
- **Observer Pattern**: GUI updates based on analysis progress
- **Factory Pattern**: Dynamic parser selection based on log format detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with detailed description