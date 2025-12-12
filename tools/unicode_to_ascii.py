#!/usr/bin/env python3
"""
Convert Unicode characters to ASCII equivalents.

This tool can convert emoji-rich markdown or text files to ASCII-only versions
for environments with limited Unicode support.
"""

import sys
import argparse
from pathlib import Path


# Mapping of Unicode characters to ASCII equivalents
UNICODE_TO_ASCII = {
    # Emojis to text
    '🎯': '[TARGET]',
    '🎓': '[LEARN]',
    '🎉': '[CELEBRATE]',
    '🐛': '[BUG]',
    '💡': '[IDEA]',
    '📊': '[CHART]',
    '📋': '[LIST]',
    '📚': '[DOCS]',
    '📝': '[NOTE]',
    '📡': '[API]',
    '📦': '[PACKAGE]',
    '🔄': '[UPDATE]',
    '🔌': '[PLUGIN]',
    '🔍': '[SEARCH]',
    '🔐': '[AUTH]',
    '🔒': '[SECURE]',
    '🔗': '[LINK]',
    '🔧': '[CONFIG]',
    '🚀': '[DEPLOY]',
    '🚨': '[ALERT]',
    '🛠️': '[TOOLS]',
    '🛡️': '[SHIELD]',
    '🤖': '[BOT]',
    '🧪': '[TEST]',
    '🌐': '[WEB]',
    '⏰': '[TIME]',
    '⚙️': '[SETTINGS]',
    '⚠️': '[WARNING]',
    
    # Check marks
    '✅': '[x]',
    '✓': '[x]',
    '✗': '[ ]',
    '❌': '[ ]',
    
    # Box drawing to ASCII art
    '─': '-',
    '│': '|',
    '├': '|',
    '└': '`',
    
    # Arrows
    '→': '->',
    
    # Variation selector (often invisible)
    '\uFE0F': '',
}


def convert_unicode_to_ascii(text, mapping=None):
    """Convert Unicode characters to ASCII equivalents."""
    if mapping is None:
        mapping = UNICODE_TO_ASCII
    
    result = text
    for unicode_char, ascii_equiv in mapping.items():
        result = result.replace(unicode_char, ascii_equiv)
    
    return result


def convert_file(input_path, output_path, mapping=None, force=False):
    """Convert a file from Unicode to ASCII."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        return False
    
    if output_path.exists() and not force:
        print(f"Error: Output file '{output_path}' already exists. Use --force to overwrite.", 
              file=sys.stderr)
        return False
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        converted = convert_unicode_to_ascii(content, mapping)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted)
        
        print(f"✓ Converted: {input_path} -> {output_path}")
        return True
    
    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)
        return False


def show_mappings():
    """Display all Unicode to ASCII mappings."""
    print("=" * 80)
    print("UNICODE TO ASCII MAPPINGS")
    print("=" * 80)
    
    print("\nEmojis:")
    for unicode_char, ascii_equiv in sorted(UNICODE_TO_ASCII.items()):
        if ord(unicode_char[0]) > 0x1F000:  # Emoji range
            print(f"  '{unicode_char}' -> '{ascii_equiv}'")
    
    print("\nCheck Marks:")
    check_marks = ['✅', '✓', '✗', '❌']
    for char in check_marks:
        if char in UNICODE_TO_ASCII:
            print(f"  '{char}' -> '{UNICODE_TO_ASCII[char]}'")
    
    print("\nBox Drawing:")
    box_chars = ['─', '│', '├', '└']
    for char in box_chars:
        if char in UNICODE_TO_ASCII:
            print(f"  '{char}' -> '{UNICODE_TO_ASCII[char]}'")
    
    print("\nArrows:")
    print(f"  '→' -> '{UNICODE_TO_ASCII['→']}'")


def main():
    parser = argparse.ArgumentParser(
        description='Convert Unicode characters to ASCII equivalents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md output.md              # Convert single file
  %(prog)s input.md output.md --force      # Overwrite existing output
  %(prog)s --show-mappings                 # Display character mappings
  
Notes:
  - Input and output files use UTF-8 encoding
  - Original Unicode characters are replaced with ASCII text equivalents
  - Box drawing characters are replaced with simple ASCII art
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file path'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        help='Output file path'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite output file if it exists'
    )
    
    parser.add_argument(
        '--show-mappings', '-m',
        action='store_true',
        help='Display Unicode to ASCII mappings and exit'
    )
    
    args = parser.parse_args()
    
    if args.show_mappings:
        show_mappings()
        return 0
    
    if not args.input or not args.output:
        parser.print_help()
        return 1
    
    success = convert_file(args.input, args.output, force=args.force)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
