#!/usr/bin/env python3
"""
Find and report Unicode characters in repository files.

This tool scans text files for non-ASCII Unicode characters and provides
detailed reports about their usage, location, and context.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import argparse


def get_char_info(char):
    """Get detailed information about a Unicode character."""
    return {
        'char': char,
        'codepoint': f"U+{ord(char):04X}",
        'decimal': ord(char),
        'name': get_char_name(char),
        'category': get_char_category(char)
    }


def get_char_name(char):
    """Get Unicode character name."""
    try:
        import unicodedata
        return unicodedata.name(char, 'UNKNOWN')
    except:
        return 'UNKNOWN'


def get_char_category(char):
    """Get Unicode character category."""
    try:
        import unicodedata
        return unicodedata.category(char)
    except:
        return 'UNKNOWN'


def find_unicode_in_file(filepath, show_context=False):
    """Find all non-ASCII characters in a file."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line_num, line in enumerate(lines, 1):
                chars_in_line = set()
                for pos, char in enumerate(line):
                    if ord(char) > 127:
                        chars_in_line.add(char)
                
                if chars_in_line:
                    result = {
                        'line': line_num,
                        'chars': sorted(chars_in_line, key=lambda x: ord(x)),
                        'content': line.rstrip()
                    }
                    if show_context:
                        result['context'] = line.strip()[:100]
                    results.append(result)
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    
    return results


def scan_directory(directory, patterns, exclude_patterns=None):
    """Scan directory for files matching patterns."""
    exclude_patterns = exclude_patterns or ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
    results = {}
    
    for pattern in patterns:
        for filepath in Path(directory).rglob(pattern):
            # Skip excluded directories
            if any(excl in str(filepath) for excl in exclude_patterns):
                continue
            
            unicode_found = find_unicode_in_file(filepath)
            if unicode_found:
                results[str(filepath)] = unicode_found
    
    return results


def print_summary(results, directory):
    """Print summary of Unicode character usage."""
    # Collect all unique characters
    all_chars = defaultdict(list)
    total_lines = 0
    
    for filepath, lines in results.items():
        total_lines += len(lines)
        for line_info in lines:
            for char in line_info['chars']:
                all_chars[char].append({
                    'file': filepath.replace(f"{directory}/", ""),
                    'line': line_info['line']
                })
    
    print("=" * 80)
    print("UNICODE CHARACTER SUMMARY")
    print("=" * 80)
    print(f"\nTotal files with Unicode: {len(results)}")
    print(f"Total lines with Unicode: {total_lines}")
    print(f"Unique Unicode characters: {len(all_chars)}")
    print("\n" + "=" * 80)
    print("ALL UNICODE CHARACTERS FOUND")
    print("=" * 80)
    
    for char in sorted(all_chars.keys(), key=lambda x: ord(x)):
        info = get_char_info(char)
        occurrences = len(all_chars[char])
        print(f"\nCharacter: '{char}'")
        print(f"  Codepoint: {info['codepoint']} (decimal: {info['decimal']})")
        print(f"  Name: {info['name']}")
        print(f"  Category: {info['category']}")
        print(f"  Occurrences: {occurrences} location(s)")


def print_detailed_report(results, directory, max_files=None):
    """Print detailed report of Unicode usage by file."""
    print("\n" + "=" * 80)
    print("DETAILED FILE REPORT")
    print("=" * 80)
    
    sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
    
    if max_files:
        sorted_results = sorted_results[:max_files]
    
    for filepath, lines in sorted_results:
        rel_path = filepath.replace(f"{directory}/", "")
        print(f"\n{'=' * 80}")
        print(f"FILE: {rel_path}")
        print(f"Lines with Unicode: {len(lines)}")
        print('-' * 80)
        
        for line_info in lines[:10]:  # Show first 10 lines
            chars_str = ', '.join([f"'{c}' ({get_char_info(c)['codepoint']})" 
                                  for c in line_info['chars']])
            print(f"  Line {line_info['line']}: {chars_str}")
            if 'context' in line_info:
                print(f"    → {line_info['content'][:80]}")
        
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more lines with Unicode")


def main():
    parser = argparse.ArgumentParser(
        description='Find and report Unicode characters in repository files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Scan current directory
  %(prog)s --directory /path/to/repo  # Scan specific directory
  %(prog)s --detailed --max-files 5   # Show detailed report for top 5 files
  %(prog)s --pattern "*.py"          # Scan only Python files
        """
    )
    
    parser.add_argument(
        '--directory', '-d',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        action='append',
        help='File patterns to include (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed file-by-file report'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        help='Limit detailed report to top N files'
    )
    
    parser.add_argument(
        '--context',
        action='store_true',
        help='Show line content context'
    )
    
    args = parser.parse_args()
    
    # Default patterns if none specified
    patterns = args.pattern or [
        '*.py', '*.md', '*.txt', '*.js', '*.json', 
        '*.yml', '*.yaml', '*.html', '*.css'
    ]
    
    directory = os.path.abspath(args.directory)
    
    print(f"Scanning directory: {directory}")
    print(f"File patterns: {', '.join(patterns)}")
    print("=" * 80)
    
    results = scan_directory(directory, patterns)
    
    if not results:
        print("\n✓ No Unicode characters found in scanned files.")
        return 0
    
    print_summary(results, directory)
    
    if args.detailed:
        print_detailed_report(results, directory, args.max_files)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
