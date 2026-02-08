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
        try:
            if not os.path.exists(home_backup_dir):
                os.makedirs(home_backup_dir)
            print(f"Note: Cannot create backup directory at {backup_dir}")
            print(f"      Using fallback location: {home_backup_dir}")
            _backup_dir_cache[file_dir] = home_backup_dir
            return home_backup_dir
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot create backup directory. Tried:\n  {backup_dir}\n  {home_backup_dir}\nError: {e}")

def get_unique_backup_path(backup_dir, filename):
    """Generate a unique backup filename if file already exists."""
    base_name, ext = os.path.splitext(filename)
    backup_path = os.path.join(backup_dir, filename)

    # If file doesn't exist, use original name
    if not os.path.exists(backup_path):
        return backup_path

    # If file exists, append counter (with safety limit)
    counter = 1
    max_attempts = 10000
    while counter < max_attempts:
        new_filename = f"{base_name}_{counter}{ext}"
        backup_path = os.path.join(backup_dir, new_filename)
        if not os.path.exists(backup_path):
            return backup_path
        counter += 1

    raise RuntimeError(f"Cannot create unique backup filename after {max_attempts} attempts")

def get_file_type(filepath):
    """Determine file type based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        return 'jpeg'
    elif ext == '.png':
        return 'png'
    else:
        return None

def get_finder_selection():
    """Get the currently selected file in Finder using AppleScript."""
    script = '''
    tell application "Finder"
        set selectedItems to selection
        if (count of selectedItems) is 0 then
            return ""
        end if
        set firstItem to item 1 of selectedItems
        return POSIX path of (firstItem as alias)
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True,
            timeout=5  # 5 second timeout
        )
        path = result.stdout.strip()

        # Validate it's a file, not a directory
        if path and os.path.isdir(path):
            return None  # Signal that selection is not a file

        return path
    except subprocess.TimeoutExpired:
        print("Warning: Finder not responding")
        return None
    except subprocess.CalledProcessError:
        return None

def rotate_with_jpegtran(filepath, direction, rotation_angle):
    """Rotate JPEG using jpegtran."""
    # Compute paths once
    abs_filepath = os.path.abspath(filepath)
    file_dir = os.path.dirname(abs_filepath)
    filename = os.path.basename(abs_filepath)

    # Check if temp directory is writable
    try:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False, dir=file_dir) as tmp:
            tmp_path = tmp.name
    except (OSError, PermissionError) as e:
        print(f"Error: Cannot create temporary file in {file_dir}: {e}")
        return False

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
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Verify temp file was created and has content
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            print("Error: Rotation produced empty or missing file")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(file_dir)
        backup_path = get_unique_backup_path(backup_dir, filename)

        try:
            shutil.copy(abs_filepath, backup_path)
        except (OSError, PermissionError, shutil.Error) as e:
            print(f"Error: Cannot create backup: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Replace original with rotated version
        os.replace(tmp_path, abs_filepath)
        print(f"✓ Rotated {abs_filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")
        return True

    except (OSError, RuntimeError) as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        return False
    except Exception as e:
        # Catch unexpected errors
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Unexpected error: {e}")
        return False

def rotate_with_imagemagick(filepath, direction, rotation_angle):
    """Rotate PNG using ImageMagick 7."""
    # Compute paths once
    abs_filepath = os.path.abspath(filepath)
    file_dir = os.path.dirname(abs_filepath)
    filename = os.path.basename(abs_filepath)

    # Check if temp directory is writable
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=file_dir) as tmp:
            tmp_path = tmp.name
    except (OSError, PermissionError) as e:
        print(f"Error: Cannot create temporary file in {file_dir}: {e}")
        return False

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
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Verify temp file was created and has content
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            print("Error: Rotation produced empty or missing file")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(file_dir)
        backup_path = get_unique_backup_path(backup_dir, filename)

        try:
            shutil.copy(abs_filepath, backup_path)
        except (OSError, PermissionError, shutil.Error) as e:
            print(f"Error: Cannot create backup: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False

        # Replace original with rotated version
        os.replace(tmp_path, abs_filepath)
        print(f"✓ Rotated {abs_filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")
        return True

    except (OSError, RuntimeError) as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        return False
    except Exception as e:
        # Catch unexpected errors
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Unexpected error: {e}")
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
        ext = os.path.splitext(filepath)[1] or "(no extension)"
        print(f"Error: Unsupported file type '{ext}'")
        print("Supported formats: .jpg, .jpeg, .png")
        return False

    # Route to appropriate rotation function based on file type
    if file_type == 'jpeg':
        return rotate_with_jpegtran(filepath, direction, rotation_map[direction])
    elif file_type == 'png':
        return rotate_with_imagemagick(filepath, direction, rotation_map[direction])

    return False

def interactive_mode():
    """Run in interactive/persistent mode."""
    print("Interactive Image Rotation Tool")
    print("=" * 40)
    print("Enter: <image_path> <direction>")
    print("Or just: <direction> (uses Finder selection)")
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

            parts = user_input.split()

            # If only one word and it's a direction, use Finder selection
            if len(parts) == 1 and parts[0].lower() in ['l', 'r', 'f']:
                direction = parts[0].lower()
                filepath = get_finder_selection()

                if not filepath:
                    print("Error: No file selected in Finder, or selection is a folder")
                    print("Tip: Select a single file in Finder, then type the direction")
                    continue

                # Validate it's actually a file
                if not os.path.isfile(filepath):
                    print(f"Error: Selected item is not a file: {filepath}")
                    continue

                print(f"Using Finder selection: {os.path.basename(filepath)}")
            elif len(parts) >= 2:
                # Original behavior: filepath + direction
                direction = parts[-1].lower()
                filepath = ' '.join(parts[:-1])

                # Remove escape characters that macOS adds when dragging files
                filepath = filepath.replace('\\ ', ' ').replace("\\'", "'")
            else:
                print("Error: Please provide <direction> or <image_path> <direction>")
                print("Example: r  (rotates Finder selection)")
                print("Example: /path/to/image.jpg r")
                continue

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
