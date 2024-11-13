import os
import frontmatter
from pathlib import Path
import yaml

def count_content_lines(file_path):
    """Count non-empty lines in the content section (excluding frontmatter)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                post = frontmatter.load(f)
                # Get content after frontmatter
                content = post.content
                # Return 0 if content is None or empty string
                if not content or content.isspace():
                    return 0
                # Count non-empty lines
                non_empty_lines = len([line for line in content.split('\n') if line.strip()])
                return non_empty_lines
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                # If frontmatter parsing fails, try counting lines in the whole file
                f.seek(0)
                non_empty_lines = len([line for line in f if line.strip()])
                return non_empty_lines
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0

def filter_empty_files(directory, min_lines=3, delete=False):
    """
    Find all markdown files with less than min_lines of content.
    If delete=True, removes the files; otherwise just prints them.
    """
    empty_files = []
    deleted_count = 0
    
    # Recursively find all .md files
    for path in Path(directory).rglob('*.md'):
        try:
            line_count = count_content_lines(path)
            if line_count < min_lines:
                empty_files.append(path)
                if delete:
                    try:
                        os.remove(path)
                        deleted_count += 1
                        print(f"Deleted: {path} (lines: {line_count})")
                    except PermissionError:
                        print(f"Permission denied when trying to delete: {path}")
                    except Exception as e:
                        print(f"Error deleting {path}: {e}")
                else:
                    print(f"Found empty file: {path} (lines: {line_count})")
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    if delete:
        print(f"\nSuccessfully deleted {deleted_count} files")
    return empty_files

# Example usage - make sure to set delete=True
directory = "topsoe_scrape"  # Adjust this to your project directory
empty_files = filter_empty_files(directory, min_lines=3, delete=True)  # Note: delete=True here
print(f"\nTotal near-empty files found: {len(empty_files)}")