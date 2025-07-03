"""
Log File Analyzer

A comprehensive Python application for analyzing log files from web servers and applications.
Provides both command-line interface (CLI) and graphical user interface (GUI) options
for parsing, filtering, and summarizing log data.

Features:
- Parse various log formats using regular expressions
- Filter logs by date range, log level, and keywords
- Generate detailed summaries and statistics
- Export results to different formats
- Interactive GUI for non-technical users

"""

import re
import argparse
import datetime
import os
import sys
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class LogEntry:
    """
    Represents a single log entry with parsed components.
    
    Attributes:
        timestamp: DateTime object representing when the log entry was created
        level: Log level (INFO, WARNING, ERROR, DEBUG, etc.)
        message: The actual log message content
        source: Source component or module that generated the log
        raw_line: Original unparsed log line
        line_number: Line number in the source file
    """
    
    def __init__(self, timestamp: datetime.datetime, level: str, message: str, 
                 source: str = "", raw_line: str = "", line_number: int = 0):
        self.timestamp = timestamp
        self.level = level.upper()
        self.message = message
        self.source = source
        self.raw_line = raw_line
        self.line_number = line_number
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'source': self.source,
            'raw_line': self.raw_line,
            'line_number': self.line_number
        }


class LogParser:
    """
    Handles parsing of various log file formats using regular expressions.
    
    Supports common log formats including:
    - Apache/Nginx access logs
    - Application logs with timestamps
    - System logs
    - Custom log formats
    """
    
    def __init__(self):
        self.patterns = {
            'apache_access': re.compile(
                r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<timestamp>[^\]]+)\] '
                r'"(?P<method>\w+) (?P<url>[^\s]+) (?P<protocol>[^"]+)" '
                r'(?P<status>\d+) (?P<size>\d+|-)'
            ),
            'application_log': re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,.]?\d*) '
                r'\[?(?P<level>\w+)\]?\s*:?\s*(?P<message>.*)'
            ),
            'system_log': re.compile(
                r'(?P<timestamp>\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) '
                r'(?P<hostname>\w+) (?P<source>\w+)(\[(?P<pid>\d+)\])?: '
                r'(?P<message>.*)'
            ),
            'iis_log': re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
                r'(?P<server_ip>\S+) (?P<method>\w+) (?P<uri>\S+) '
                r'(?P<query>\S+) (?P<port>\d+) (?P<username>\S+) '
                r'(?P<client_ip>\S+) (?P<user_agent>\S+) (?P<referer>\S+) '
                r'(?P<status>\d+) (?P<substatus>\d+) (?P<win32_status>\d+) '
                r'(?P<time_taken>\d+)'
            )
        }
        
        self.timestamp_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S,%f',
            '%d/%b/%Y:%H:%M:%S %z',
            '%b %d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
    
    def parse_timestamp(self, timestamp_str: str) -> Optional[datetime.datetime]:
        """
        Parse timestamp string using multiple format attempts.
        
        Args:
            timestamp_str: String representation of timestamp
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        timestamp_str = timestamp_str.strip()
        
        for fmt in self.timestamp_formats:
            try:
                if fmt.endswith('%z') and '+' not in timestamp_str and 'Z' not in timestamp_str:
                    timestamp_str += ' +0000'
                return datetime.datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        try:
            return datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def parse_line(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """
        Parse a single log line using available patterns.
        
        Args:
            line: Log line to parse
            line_number: Line number in source file
            
        Returns:
            LogEntry object or None if parsing fails
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        for pattern_name, pattern in self.patterns.items():
            match = pattern.match(line)
            if match:
                groups = match.groupdict()
                
                timestamp = self.parse_timestamp(groups.get('timestamp', ''))
                if not timestamp:
                    timestamp = datetime.datetime.now()
                
                if pattern_name == 'apache_access':
                    level = 'INFO' if int(groups.get('status', '0')) < 400 else 'ERROR'
                    message = f"{groups.get('method')} {groups.get('url')} - {groups.get('status')}"
                    source = 'apache'
                elif pattern_name == 'system_log':
                    level = 'INFO'
                    message = groups.get('message', '')
                    source = groups.get('source', '')
                else:
                    level = groups.get('level', 'INFO')
                    message = groups.get('message', '')
                    source = groups.get('source', '')
                
                return LogEntry(
                    timestamp=timestamp,
                    level=level,
                    message=message,
                    source=source,
                    raw_line=line,
                    line_number=line_number
                )
        
        fallback_match = re.search(r'(ERROR|WARN|INFO|DEBUG|TRACE|FATAL)', line, re.IGNORECASE)
        if fallback_match:
            level = fallback_match.group(1)
            timestamp = datetime.datetime.now()
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=line,
                source='unknown',
                raw_line=line,
                line_number=line_number
            )
        
        return LogEntry(
            timestamp=datetime.datetime.now(),
            level='INFO',
            message=line,
            source='unknown',
            raw_line=line,
            line_number=line_number
        )


class LogAnalyzer:
    """
    Main analyzer class for processing and analyzing log files.
    
    Provides functionality for:
    - Loading and parsing log files
    - Filtering logs by various criteria
    - Generating statistics and summaries
    - Exporting results
    """
    
    def __init__(self):
        self.parser = LogParser()
        self.entries: List[LogEntry] = []
        self.stats: Dict[str, Any] = {}
    
    def load_file(self, file_path: str) -> Tuple[int, int]:
        """
        Load and parse log file.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            Tuple of (total_lines, parsed_entries)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        self.entries.clear()
        total_lines = 0
        parsed_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_number, line in enumerate(file, 1):
                    total_lines += 1
                    entry = self.parser.parse_line(line, line_number)
                    if entry:
                        self.entries.append(entry)
                        parsed_count += 1
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        
        self.generate_statistics()
        return total_lines, parsed_count
    
    def filter_entries(self, start_date: Optional[datetime.datetime] = None,
                      end_date: Optional[datetime.datetime] = None,
                      levels: Optional[List[str]] = None,
                      keywords: Optional[List[str]] = None,
                      source: Optional[str] = None) -> List[LogEntry]:
        """
        Filter log entries based on specified criteria.
        
        Args:
            start_date: Filter entries after this date
            end_date: Filter entries before this date
            levels: List of log levels to include
            keywords: List of keywords to search for in messages
            source: Source component to filter by
            
        Returns:
            List of filtered LogEntry objects
        """
        filtered = self.entries
        
        if start_date:
            filtered = [e for e in filtered if e.timestamp >= start_date]
        
        if end_date:
            filtered = [e for e in filtered if e.timestamp <= end_date]
        
        if levels:
            levels_upper = [level.upper() for level in levels]
            filtered = [e for e in filtered if e.level in levels_upper]
        
        if keywords:
            keyword_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]
            filtered = [e for e in filtered 
                       if any(pattern.search(e.message) for pattern in keyword_patterns)]
        
        if source:
            filtered = [e for e in filtered if source.lower() in e.source.lower()]
        
        return filtered
    
    def generate_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistics from loaded log entries.
        
        Returns:
            Dictionary containing various statistics
        """
        if not self.entries:
            self.stats = {}
            return self.stats
        
        level_counts = Counter(entry.level for entry in self.entries)
        source_counts = Counter(entry.source for entry in self.entries)
        
        timestamps = [entry.timestamp for entry in self.entries]
        date_counts = Counter(ts.date() for ts in timestamps)
        hour_counts = Counter(ts.hour for ts in timestamps)
        
        error_entries = [e for e in self.entries if e.level in ['ERROR', 'FATAL']]
        warning_entries = [e for e in self.entries if e.level == 'WARNING']
        
        self.stats = {
            'total_entries': len(self.entries),
            'level_distribution': dict(level_counts),
            'source_distribution': dict(source_counts),
            'date_distribution': {str(k): v for k, v in date_counts.items()},
            'hourly_distribution': dict(hour_counts),
            'error_count': len(error_entries),
            'warning_count': len(warning_entries),
            'error_rate': len(error_entries) / len(self.entries) * 100,
            'warning_rate': len(warning_entries) / len(self.entries) * 100,
            'date_range': {
                'start': min(timestamps).isoformat() if timestamps else None,
                'end': max(timestamps).isoformat() if timestamps else None
            },
            'top_error_messages': [entry.message for entry in error_entries[:10]],
            'top_warning_messages': [entry.message for entry in warning_entries[:10]]
        }
        
        return self.stats
    
    def export_results(self, output_path: str, entries: List[LogEntry], 
                      format_type: str = 'json') -> bool:
        """
        Export filtered results to specified format.
        
        Args:
            output_path: Path for output file
            entries: List of log entries to export
            format_type: Export format ('json', 'csv', 'txt')
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if format_type.lower() == 'json':
                data = {
                    'metadata': {
                        'export_time': datetime.datetime.now().isoformat(),
                        'entry_count': len(entries),
                        'statistics': self.stats
                    },
                    'entries': [entry.to_dict() for entry in entries]
                }
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format_type.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Level', 'Source', 'Message', 'Line Number'])
                    for entry in entries:
                        writer.writerow([
                            entry.timestamp.isoformat(),
                            entry.level,
                            entry.source,
                            entry.message,
                            entry.line_number
                        ])
            
            elif format_type.lower() == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Log Analysis Report\n")
                    f.write(f"Generated: {datetime.datetime.now()}\n")
                    f.write(f"Total Entries: {len(entries)}\n\n")
                    
                    for entry in entries:
                        f.write(f"{entry}\n")
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False


class LogAnalyzerGUI:
    """
    Graphical User Interface for the Log File Analyzer.
    
    Provides an intuitive interface for non-technical users to:
    - Load log files
    - Apply filters
    - View results
    - Export data
    """
    
    def __init__(self):
        self.analyzer = LogAnalyzer()
        self.filtered_entries = []
        
        self.root = tk.Tk()
        self.root.title("Log File Analyzer")
        self.root.geometry("1200x800")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Initialize and configure the GUI components."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        ttk.Label(main_frame, text="Log File Analyzer", 
                 font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Log File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)
        ttk.Button(file_frame, text="Load", command=self.load_file).grid(row=0, column=3, padx=(10, 0))
        
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="10")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.start_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.start_date_var, width=20).grid(
            row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(filter_frame, text="End Date:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.end_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.end_date_var, width=20).grid(
            row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Log Levels:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.levels_frame = ttk.Frame(filter_frame)
        self.levels_frame.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        self.level_vars = {}
        levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
        for i, level in enumerate(levels):
            var = tk.BooleanVar(value=True)
            self.level_vars[level] = var
            ttk.Checkbutton(self.levels_frame, text=level, variable=var).grid(
                row=0, column=i, padx=(0, 10))
        
        ttk.Label(filter_frame, text="Keywords:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.keywords_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.keywords_var, width=30).grid(
            row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Source:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.source_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.source_var, width=20).grid(
            row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(
            row=5, column=0, columnspan=2, pady=(10, 0))
        
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=80, height=30)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        export_frame = ttk.Frame(results_frame)
        export_frame.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)
        
        ttk.Label(export_frame, text="Export Format:").grid(row=0, column=0, padx=(0, 10))
        self.export_format_var = tk.StringVar(value="json")
        ttk.Combobox(export_frame, textvariable=self.export_format_var, 
                    values=["json", "csv", "txt"], width=10).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(export_frame, text="Export Results", command=self.export_results).grid(row=0, column=2)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def browse_file(self):
        """Open file dialog to select log file."""
        file_path = filedialog.askopenfilename(
            title="Select Log File",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_file(self):
        """Load and parse the selected log file."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a log file first.")
            return
        
        try:
            self.status_var.set("Loading file...")
            self.root.update()
            
            total_lines, parsed_count = self.analyzer.load_file(file_path)
            
            self.status_var.set(f"Loaded {parsed_count} entries from {total_lines} lines")
            self.display_statistics()
            self.apply_filters()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.status_var.set("Ready")
    
    def apply_filters(self):
        """Apply current filter settings to log entries."""
        if not self.analyzer.entries:
            return
        
        try:
            start_date = None
            end_date = None
            
            if self.start_date_var.get():
                start_date = datetime.datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            
            if self.end_date_var.get():
                end_date = datetime.datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
            
            selected_levels = [level for level, var in self.level_vars.items() if var.get()]
            
            keywords = []
            if self.keywords_var.get():
                keywords = [kw.strip() for kw in self.keywords_var.get().split(',') if kw.strip()]
            
            source = self.source_var.get().strip() if self.source_var.get().strip() else None
            
            self.filtered_entries = self.analyzer.filter_entries(
                start_date=start_date,
                end_date=end_date,
                levels=selected_levels,
                keywords=keywords,
                source=source
            )
            
            self.display_results()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    
    def display_statistics(self):
        """Display file statistics in the results area."""
        stats = self.analyzer.stats
        if not stats:
            return
        
        output = "FILE STATISTICS\n"
        output += "=" * 50 + "\n\n"
        output += f"Total Entries: {stats['total_entries']}\n"
        output += f"Error Rate: {stats['error_rate']:.2f}%\n"
        output += f"Warning Rate: {stats['warning_rate']:.2f}%\n\n"
        
        output += "Log Level Distribution:\n"
        for level, count in stats['level_distribution'].items():
            output += f"  {level}: {count}\n"
        
        output += "\nSource Distribution:\n"
        for source, count in list(stats['source_distribution'].items())[:10]:
            output += f"  {source}: {count}\n"
        
        if stats['date_range']['start']:
            output += f"\nDate Range: {stats['date_range']['start']} to {stats['date_range']['end']}\n"
        
        output += "\n" + "=" * 50 + "\n\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
    
    def display_results(self):
        """Display filtered log entries in the results area."""
        self.results_text.delete(1.0, tk.END)
        
        if not self.filtered_entries:
            self.results_text.insert(tk.END, "No entries match the current filters.\n")
            return
        
        output = f"FILTERED RESULTS ({len(self.filtered_entries)} entries)\n"
        output += "=" * 50 + "\n\n"
        
        for entry in self.filtered_entries[:1000]:
            output += f"[{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            output += f"{entry.level:8} | {entry.source:15} | {entry.message}\n"
        
        if len(self.filtered_entries) > 1000:
            output += f"\n... and {len(self.filtered_entries) - 1000} more entries\n"
        
        self.results_text.insert(tk.END, output)
        self.status_var.set(f"Displaying {min(len(self.filtered_entries), 1000)} of {len(self.filtered_entries)} filtered entries")
    
    def export_results(self):
        """Export filtered results to file."""
        if not self.filtered_entries:
            messagebox.showwarning("Warning", "No results to export.")
            return
        
        format_type = self.export_format_var.get()
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=f".{format_type}",
            filetypes=[
                (f"{format_type.upper()} files", f"*.{format_type}"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            if self.analyzer.export_results(file_path, self.filtered_entries, format_type):
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export results.")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create and configure command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Log File Analyzer - Parse and analyze log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python log_analyzer.py access.log
  python log_analyzer.py --file app.log --level ERROR WARNING
  python log_analyzer.py --file server.log --start-date 2024-01-01 --end-date 2024-01-31
  python log_analyzer.py --file app.log --keywords "timeout,connection" --export results.json
  python log_analyzer.py --gui
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Path to the log file to analyze'
    )
    
    parser.add_argument(
        '--file', '-f',
        dest='file_path',
        help='Path to the log file to analyze (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for filtering (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for filtering (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--level', '-l',
        nargs='+',
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'FATAL'],
        help='Log levels to include in analysis'
    )
    
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        help='Comma-separated keywords to search for in log messages'
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        help='Filter by source component'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export results to file (format determined by extension)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'txt'],
        default='json',
        help='Export format (default: json)'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show only statistics, not individual log entries'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch graphical user interface'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Log File Analyzer 1.0.0'
    )
    
    return parser


def print_statistics(stats: Dict[str, Any]):
    """
    Print formatted statistics to console.
    
    Args:
        stats: Statistics dictionary from LogAnalyzer
    """
    print("\nLOG FILE STATISTICS")
    print("=" * 50)
    print(f"Total Entries: {stats['total_entries']:,}")
    print(f"Error Rate: {stats['error_rate']:.2f}%")
    print(f"Warning Rate: {stats['warning_rate']:.2f}%")
    
    print("\nLog Level Distribution:")
    for level, count in stats['level_distribution'].items():
        percentage = (count / stats['total_entries']) * 100
        print(f"  {level:10}: {count:8,} ({percentage:5.1f}%)")
    
    print("\nTop Sources:")
    source_items = list(stats['source_distribution'].items())
    source_items.sort(key=lambda x: x[1], reverse=True)
    for source, count in source_items[:10]:
        print(f"  {source:20}: {count:,}")
    
    if stats['date_range']['start']:
        print(f"\nDate Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    
    print("\nHourly Distribution:")
    for hour in range(24):
        count = stats['hourly_distribution'].get(hour, 0)
        if count > 0:
            print(f"  {hour:02d}:00 - {hour:02d}:59: {count:,}")


def print_entries(entries: List[LogEntry], limit: int = 100):
    """
    Print formatted log entries to console.
    
    Args:
        entries: List of LogEntry objects to print
        limit: Maximum number of entries to print
    """
    print(f"\nLOG ENTRIES ({len(entries)} total, showing first {min(len(entries), limit)})")
    print("=" * 100)
    
    for i, entry in enumerate(entries[:limit]):
        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp_str}] {entry.level:8} | {entry.source:15} | {entry.message}")
    
    if len(entries) > limit:
        print(f"\n... and {len(entries) - limit} more entries")


def main():
    """Main entry point for the application."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if args.gui:
        try:
            app = LogAnalyzerGUI()
            app.run()
        except ImportError:
            print("Error: tkinter is required for GUI mode but not available.")
            print("Please install tkinter or use CLI mode instead.")
            sys.exit(1)
        return
    
    file_path = args.file or args.file_path
    if not file_path:
        print("Error: No log file specified. Use --file or provide file as positional argument.")
        print("Use --help for usage information or --gui for graphical interface.")
        sys.exit(1)
    
    analyzer = LogAnalyzer()
    
    try:
        print(f"Loading log file: {file_path}")
        total_lines, parsed_count = analyzer.load_file(file_path)
        print(f"Loaded {parsed_count:,} entries from {total_lines:,} lines")
        
    except FileNotFoundError:
        print(f"Error: Log file not found: {file_path}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading file: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid start date format: {args.start_date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    if args.end_date:
        try:
            end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            print(f"Error: Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    keywords = []
    if args.keywords:
        keywords = [kw.strip() for kw in args.keywords.split(',') if kw.strip()]
    
    filtered_entries = analyzer.filter_entries(
        start_date=start_date,
        end_date=end_date,
        levels=args.level,
        keywords=keywords,
        source=args.source
    )
    
    print_statistics(analyzer.stats)
    
    if not args.stats_only:
        print_entries(filtered_entries)
    
    if args.export:
        export_format = args.format
        if '.' in args.export:
            export_format = args.export.split('.')[-1]
        
        if analyzer.export_results(args.export, filtered_entries, export_format):
            print(f"\nResults exported to: {args.export}")
        else:
            print(f"\nError: Failed to export results to: {args.export}")
            sys.exit(1)


if __name__ == "__main__":
    main()
