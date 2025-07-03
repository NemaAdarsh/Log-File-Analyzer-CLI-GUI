"""
Test suite and demonstration script for Log File Analyzer.

This script demonstrates the functionality of the log analyzer
and can be used to verify that all features work correctly.
"""

import os
import sys
import datetime
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_analyzer import LogAnalyzer, LogParser, LogEntry


def create_test_log():
    """Create a temporary test log file with various log formats."""
    test_content = """2024-01-15 10:30:25.123 [INFO]: Application started successfully
2024-01-15 10:30:26.456 [WARNING]: High memory usage detected
2024-01-15 10:30:27.789 [ERROR]: Database connection failed
2024-01-15 10:30:28.012 [INFO]: Retrying database connection
2024-01-15 10:30:29.345 [ERROR]: Connection retry failed
2024-01-15 10:30:30.678 [FATAL]: System shutdown initiated
192.168.1.100 - - [15/Jan/2024:10:30:31 -0700] "GET /index.html HTTP/1.1" 200 2326
192.168.1.101 - - [15/Jan/2024:10:30:32 -0700] "POST /login HTTP/1.1" 401 234
192.168.1.102 - - [15/Jan/2024:10:30:33 -0700] "GET /admin HTTP/1.1" 403 145
Jan 15 10:30:34 server01 apache[1234]: Configuration reloaded
Jan 15 10:30:35 server01 mysql[5678]: Database connection restored"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    return temp_file.name


def test_basic_parsing():
    """Test basic log parsing functionality."""
    print("Testing Basic Parsing...")
    print("-" * 40)
    
    parser = LogParser()
    
    test_lines = [
        "2024-01-15 10:30:25.123 [INFO]: Application started",
        "2024-01-15 10:30:26.456 [ERROR]: Database failed",
        "192.168.1.100 - - [15/Jan/2024:10:30:27 -0700] \"GET /test HTTP/1.1\" 200 1234"
    ]
    
    for i, line in enumerate(test_lines, 1):
        entry = parser.parse_line(line, i)
        if entry:
            print(f"Line {i}: {entry.level} - {entry.message[:50]}...")
        else:
            print(f"Line {i}: Failed to parse")
    
    print()


def test_file_analysis():
    """Test complete file analysis workflow."""
    print("Testing File Analysis...")
    print("-" * 40)
    
    test_file = create_test_log()
    
    try:
        analyzer = LogAnalyzer()
        total_lines, parsed_count = analyzer.load_file(test_file)
        
        print(f"Total lines: {total_lines}")
        print(f"Parsed entries: {parsed_count}")
        print(f"Parse success rate: {(parsed_count/total_lines)*100:.1f}%")
        
        stats = analyzer.generate_statistics()
        print(f"Error count: {stats['error_count']}")
        print(f"Warning count: {stats['warning_count']}")
        print(f"Error rate: {stats['error_rate']:.1f}%")
        
        print("\nLevel distribution:")
        for level, count in stats['level_distribution'].items():
            print(f"  {level}: {count}")
        
        print()
        
    finally:
        os.unlink(test_file)


def test_filtering():
    """Test log filtering functionality."""
    print("Testing Filtering...")
    print("-" * 40)
    
    test_file = create_test_log()
    
    try:
        analyzer = LogAnalyzer()
        analyzer.load_file(test_file)
        
        print("All entries:")
        print(f"  Total: {len(analyzer.entries)}")
        
        error_entries = analyzer.filter_entries(levels=['ERROR', 'FATAL'])
        print(f"Error/Fatal entries: {len(error_entries)}")
        
        database_entries = analyzer.filter_entries(keywords=['database', 'connection'])
        print(f"Database-related entries: {len(database_entries)}")
        
        today = datetime.datetime.now().date()
        today_entries = analyzer.filter_entries(
            start_date=datetime.datetime.combine(today, datetime.time.min),
            end_date=datetime.datetime.combine(today, datetime.time.max)
        )
        print(f"Today's entries: {len(today_entries)}")
        
        print()
        
    finally:
        os.unlink(test_file)


def test_export():
    """Test export functionality."""
    print("Testing Export...")
    print("-" * 40)
    
    test_file = create_test_log()
    
    try:
        analyzer = LogAnalyzer()
        analyzer.load_file(test_file)
        
        error_entries = analyzer.filter_entries(levels=['ERROR', 'FATAL'])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json_path = json_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as csv_file:
            csv_path = csv_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as txt_file:
            txt_path = txt_file.name
        
        try:
            json_success = analyzer.export_results(json_path, error_entries, 'json')
            csv_success = analyzer.export_results(csv_path, error_entries, 'csv')
            txt_success = analyzer.export_results(txt_path, error_entries, 'txt')
            
            print(f"JSON export: {'Success' if json_success else 'Failed'}")
            print(f"CSV export: {'Success' if csv_success else 'Failed'}")
            print(f"TXT export: {'Success' if txt_success else 'Failed'}")
            
            if json_success and os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    print(f"JSON file contains {len(data['entries'])} entries")
            
            print()
            
        finally:
            for path in [json_path, csv_path, txt_path]:
                if os.path.exists(path):
                    os.unlink(path)
        
    finally:
        os.unlink(test_file)


def test_timestamp_parsing():
    """Test various timestamp format parsing."""
    print("Testing Timestamp Parsing...")
    print("-" * 40)
    
    parser = LogParser()
    
    timestamp_tests = [
        "2024-01-15 10:30:25",
        "2024-01-15 10:30:25.123",
        "2024-01-15 10:30:25,456",
        "15/Jan/2024:10:30:25 -0700",
        "Jan 15 10:30:25",
        "2024-01-15T10:30:25",
        "2024-01-15T10:30:25.123Z"
    ]
    
    for ts_str in timestamp_tests:
        result = parser.parse_timestamp(ts_str)
        status = "Success" if result else "Failed"
        print(f"  {ts_str:25} -> {status}")
    
    print()


def run_comprehensive_demo():
    """Run a comprehensive demonstration of all features."""
    print("LOG FILE ANALYZER - COMPREHENSIVE DEMO")
    print("=" * 50)
    print()
    
    test_basic_parsing()
    test_timestamp_parsing()
    test_file_analysis()
    test_filtering()
    test_export()
    
    print("Demo completed successfully!")
    print()
    print("To test with sample files, run:")
    print("  python log_analyzer.py sample_logs/application.log")
    print("  python log_analyzer.py --gui")
    print()
    print("For help with command-line options:")
    print("  python log_analyzer.py --help")


if __name__ == "__main__":
    run_comprehensive_demo()
