#!/usr/bin/env python3
"""
Quick image rotation script using jpegtran for JPEG and ImageMagick 7 for PNG.
Usage: python rotate_jpeg.py <path_to_image> <direction>
Direction: l (90° left/CCW), r (90° right/CW), f (flip 180°)
Supported formats: JPEG (.jpg, .jpeg), PNG (.png)
"""

import sys
import subprocess
import os
import tempfile
import shutil

def ensure_backup_dir(filepath):
    """Ensure backup directory exists, with fallback to home directory."""
    file_dir = os.path.dirname(os.path.abspath(filepath))
    backup_dir = os.path.join(file_dir, 'rotate_bkup')

    # Try to create backup directory in the same location as the file
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir
    except (OSError, PermissionError):
        # Fallback to home directory if we can't create directory locally
        home_backup_dir = os.path.expanduser('~/rotate_bkup')
        if not os.path.exists(home_backup_dir):
            os.makedirs(home_backup_dir)
        print(f"Note: Cannot create backup directory at {backup_dir}")
        print(f"      Using fallback location: {home_backup_dir}")
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

def rotate_jpeg(filepath, direction):
    """Rotate JPEG file losslessly using jpegtran."""

    # Map direction to jpegtran rotation argument
    rotation_map = {
        'l': '270',  # 90° counter-clockwise = 270° clockwise
        'r': '90',   # 90° clockwise
        'f': '180'   # 180° flip
    }

    if direction not in rotation_map:
        print(f"Error: Invalid direction '{direction}'. Use 'l', 'r', or 'f'")
        sys.exit(1)

    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Check file type
    file_type = get_file_type(filepath)
    if file_type is None:
        print("Error: Currently only jpeg and png files are supported")
        sys.exit(1)

    # Route to appropriate rotation function based on file type
    if file_type == 'jpeg':
        rotate_with_jpegtran(filepath, direction, rotation_map[direction])
    elif file_type == 'png':
        rotate_with_imagemagick(filepath, direction, rotation_map[direction])

def rotate_with_jpegtran(filepath, direction, rotation_angle):
    """Rotate JPEG using jpegtran."""
    # Create temporary file in the same directory as the target file
    file_dir = os.path.dirname(os.path.abspath(filepath))
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
            filepath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running jpegtran: {result.stderr}")
            sys.exit(1)

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(filepath)
        backup_path = get_unique_backup_path(backup_dir, os.path.basename(filepath))
        shutil.copy2(filepath, backup_path)

        # Replace original with rotated version
        os.replace(tmp_path, filepath)
        print(f"✓ Rotated {filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        sys.exit(1)

def rotate_with_imagemagick(filepath, direction, rotation_angle):
    """Rotate PNG using ImageMagick 7."""
    # Create temporary file in the same directory as the target file
    file_dir = os.path.dirname(os.path.abspath(filepath))
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=file_dir) as tmp:
        tmp_path = tmp.name

    try:
        # Run ImageMagick 7 (magick command)
        cmd = [
            'magick',
            'convert',
            filepath,
            '-rotate', rotation_angle,
            tmp_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running ImageMagick: {result.stderr}")
            sys.exit(1)

        # Copy original to backup directory before replacing
        backup_dir = ensure_backup_dir(filepath)
        backup_path = get_unique_backup_path(backup_dir, os.path.basename(filepath))
        shutil.copy2(filepath, backup_path)

        # Replace original with rotated version
        os.replace(tmp_path, filepath)
        print(f"✓ Rotated {filepath} ({direction})")
        print(f"  Original backed up to: {backup_path}")

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python rotate_jpeg.py <image_file> <direction>")
        print("Direction: l (90° CCW), r (90° CW), f (180°)")
        print("Supported formats: JPEG (.jpg, .jpeg), PNG (.png)")
        sys.exit(1)

    image_file = sys.argv[1]
    direction = sys.argv[2].lower()

    rotate_jpeg(image_file, direction)
