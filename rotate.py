#!/usr/bin/env python3
"""
Image rotation tool for JPEG and PNG files.
Usage:
  rotate.py <image_path> <direction>     - Rotate once and exit
  rotate.py -p                            - Interactive mode (persistent)
Direction: l (90° left/CCW), r (90° right/CW), f (flip 180°)
Supported formats: JPEG (.jpg, .jpeg), PNG (.png)
"""

import sys
import subprocess
import os
import tempfile
import shutil

# Cache for backup directories to avoid repeated checks
_backup_dir_cache = {}

def ensure_backup_dir(file_dir):
    """Ensure backup directory exists, with fallback to home directory. Cached for speed."""
    # Check cache first
    if file_dir in _backup_dir_cache:
        return _backup_dir_cache[file_dir]

    backup_dir = os.path.join(file_dir, 'rotate_bkup')

    # Try to create backup directory in the same location as the file
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        _backup_dir_cache[file_dir] = backup_dir
        return backup_dir
    except (OSError, PermissionError):
        # Fallback to home directory if we can't create directory locally
        home_backup_dir = os.path.expanduser('~/rotate_bkup')
        if not os.path.exists(home_backup_dir):
            os.makedirs(home_backup_dir)
        print(f"Note: Cannot create backup directory at {backup_dir}")
        print(f"      Using fallback location: {home_backup_dir}")
        _backup_dir_cache[file_dir] = home_backup_dir
        return home_backup_dir

def get_unique_backup_path(backup_dir, filename):
    """Generate a unique backup filename if file already exists."""
    base_name, ext = os.path.splitext(filename)
    backup_path = os.path.join(backup_dir, filename)

    # If file doesn't exist, use original name
    if not os.path.exists(backup_path):
        return backup_path

    # If file exists, append counter
    counter = 1
    while True:
        new_filename = f"{base_name}_{counter}{ext}"
        backup_path = os.path.join(backup_dir, new_filename)
        if not os.path.exists(backup_path):
            return backup_path
        counter += 1

def get_file_type(filepath):
    """Determine file type based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        return 'jpeg'
    elif ext == '.png':
        return 'png'
    else:
        return None

def rotate_with_jpegtran(filepath, direction, rotation_angle):
    """Rotate JPEG using jpegtran."""
    # Compute paths once
    abs_filepath = os.path.abspath(filepath)
    file_dir = os.path.dirname(abs_filepath)
    filename = os.path.basename(abs_filepath)

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False, dir=file_dir) as tmp:
        tmp_path = tmp.name

    try:
        # Run jpegtran
        cmd = [
            'jpegtran',
            '-rotate', rotation_angle,
            '-copy', 'all',  # Copy all metadata
            '-trim',         # Handle partial blocks
            '-outfile', tmp_path,
            abs_filepath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running jpegtran: {result.stderr}")
            return False

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(file_dir)
        backup_path = get_unique_backup_path(backup_dir, filename)
        shutil.copy(abs_filepath, backup_path)  # Use copy instead of copy2 for speed

        # Replace original with rotated version
        os.replace(tmp_path, abs_filepath)
        print(f"✓ Rotated {abs_filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")
        return True

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        return False

def rotate_with_imagemagick(filepath, direction, rotation_angle):
    """Rotate PNG using ImageMagick 7."""
    # Compute paths once
    abs_filepath = os.path.abspath(filepath)
    file_dir = os.path.dirname(abs_filepath)
    filename = os.path.basename(abs_filepath)

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=file_dir) as tmp:
        tmp_path = tmp.name

    try:
        # Run ImageMagick 7 (magick command)
        cmd = [
            'magick',
            'convert',
            abs_filepath,
            '-rotate', rotation_angle,
            tmp_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running ImageMagick: {result.stderr}")
            return False

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(file_dir)
        backup_path = get_unique_backup_path(backup_dir, filename)
        shutil.copy(abs_filepath, backup_path)  # Use copy instead of copy2 for speed

        # Replace original with rotated version
        os.replace(tmp_path, abs_filepath)
        print(f"✓ Rotated {abs_filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")
        return True

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        return False

def rotate_image(filepath, direction):
    """Rotate image file based on type."""
    # Map direction to rotation argument
    rotation_map = {
        'l': '270',  # 90° counter-clockwise = 270° clockwise
        'r': '90',   # 90° clockwise
        'f': '180'   # 180° flip
    }

    if direction not in rotation_map:
        print(f"Error: Invalid direction '{direction}'. Use 'l', 'r', or 'f'")
        return False

    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    # Check file type
    file_type = get_file_type(filepath)
    if file_type is None:
        print("Error: Currently only jpeg and png files are supported")
        return False

    # Route to appropriate rotation function based on file type
    if file_type == 'jpeg':
        return rotate_with_jpegtran(filepath, direction, rotation_map[direction])
    elif file_type == 'png':
        return rotate_with_imagemagick(filepath, direction, rotation_map[direction])

def interactive_mode():
    """Run in interactive/persistent mode."""
    print("Interactive Image Rotation Tool")
    print("=" * 40)
    print("Enter: <image_path> <direction>")
    print("Direction: l (left), r (right), f (flip)")
    print("Type 'exit' or 'quit' to stop")
    print("=" * 40)
    print()

    while True:
        try:
            # Get user input
            user_input = input(">> ").strip()

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            # Skip empty input
            if not user_input:
                continue

            # Parse input - handle paths with spaces
            # The direction is always the last word, filepath is everything before it
            parts = user_input.split()
            if len(parts) < 2:
                print("Error: Please provide <image_path> <direction>")
                print("Example: /path/to/image.jpg r")
                continue

            direction = parts[-1].lower()
            filepath = ' '.join(parts[:-1])

            # Remove escape characters that macOS adds when dragging files
            filepath = filepath.replace('\\ ', ' ').replace("\\'", "'")

            # Rotate the image
            rotate_image(filepath, direction)
            print()  # Blank line for readability

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def main():
    """Main entry point."""
    # Check for persistent mode flag
    if len(sys.argv) == 2 and sys.argv[1] == '-p':
        interactive_mode()
    elif len(sys.argv) == 3:
        # Single rotation mode
        image_file = sys.argv[1]
        direction = sys.argv[2].lower()
        rotate_image(image_file, direction)
    else:
        print("Usage:")
        print("  rotate.py <image_file> <direction>  - Rotate once")
        print("  rotate.py -p                         - Interactive mode")
        print()
        print("Direction: l (90° CCW), r (90° CW), f (180°)")
        print("Supported formats: JPEG (.jpg, .jpeg), PNG (.png)")
        sys.exit(1)

if __name__ == '__main__':
    main()
