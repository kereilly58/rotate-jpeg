#!/usr/bin/env python3
"""
Quick JPEG rotation script using jpegtran for lossless rotation.
Usage: python rotate_jpeg.py <path_to_jpeg> <direction>
Direction: l (90° left/CCW), r (90° right/CW), f (flip 180°)
"""

import sys
import subprocess
import os
import tempfile

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

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Run jpegtran
        cmd = [
            'jpegtran',
            '-rotate', rotation_map[direction],
            '-copy', 'all',  # Copy all metadata
            '-trim',         # Handle partial blocks
            '-outfile', tmp_path,
            filepath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error running jpegtran: {result.stderr}")
            sys.exit(1)

        # Replace original with rotated version
        os.replace(tmp_path, filepath)
        print(f"✓ Rotated {filepath} ({direction})")

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python rotate_jpeg.py <jpeg_file> <direction>")
        print("Direction: l (90° CCW), r (90° CW), f (180°)")
        sys.exit(1)

    jpeg_file = sys.argv[1]
    direction = sys.argv[2].lower()

    rotate_jpeg(jpeg_file, direction)
