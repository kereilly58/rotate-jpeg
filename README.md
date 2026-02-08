# Rotate

A fast, optimized command-line tool to rotate JPEG and PNG images with automatic backup.

## Features

- **Lossless JPEG rotation** using jpegtran (preserves quality and metadata)
- **PNG rotation** using ImageMagick 7
- **Automatic backups** - originals saved to `rotate_bkup` directory
- **Two modes:**
  - Single rotation mode - rotate one image and exit
  - Interactive mode (-p flag) - process multiple images continuously
- **Finder integration (macOS)** - select files in Finder, type just the rotation direction
- **Optimized for speed** - caching and fast file operations
- **Smart backup handling** - unique filenames to prevent overwrites
- **Robust error handling** - validates files, handles permissions, prevents data loss
- **Drag-and-drop friendly** - handles file paths with spaces and special characters

## Requirements

- Python 3
- jpegtran (for JPEG rotation)
- ImageMagick 7 (for PNG rotation)

### Installing Dependencies

**macOS:**
```bash
brew install jpeg imagemagick
```

**Linux:**
```bash
sudo apt-get install libjpeg-turbo-progs imagemagick
```

## Usage

### Single Rotation Mode
Rotate one image and exit:
```bash
./rotate.py <image_file> <direction>
```

### Interactive Mode (Persistent)
Process multiple images continuously:
```bash
./rotate.py -p
```

In interactive mode, you have two options:
1. **Finder integration (macOS):** Select a file in Finder, then just type the direction (`r`, `l`, or `f`)
2. **Traditional:** Drag and drop files or type the full path followed by the direction

Type `exit`, `quit`, or `q` to stop.

## Rotation Directions

- `l` - Rotate 90° left (counter-clockwise)
- `r` - Rotate 90° right (clockwise)
- `f` - Flip 180°

## Examples

**Single rotation:**
```bash
./rotate.py photo.jpg r              # Rotate right 90°
./rotate.py image.png l              # Rotate left 90°
./rotate.py picture.jpeg f           # Flip 180°
```

**Interactive mode with Finder selection (macOS):**
```bash
./rotate.py -p
# Select a file in Finder, then just type the direction:
>> r
Using Finder selection: photo.jpg
✓ Rotated /Volumes/photos/photo.jpg (r)
  Original backed up to: /Volumes/photos/rotate_bkup/photo.jpg

>> exit
Goodbye!
```

**Interactive mode with full paths:**
```bash
./rotate.py -p
>> /Volumes/photos/image1.jpg r
✓ Rotated /Volumes/photos/image1.jpg (r)
  Original backed up to: /Volumes/photos/rotate_bkup/image1.jpg

>> /path/to/image2.png l
✓ Rotated /path/to/image2.png (l)
  Original backed up to: /path/to/rotate_bkup/image2.png

>> exit
Goodbye!
```

## Backup Behavior

- Originals are automatically backed up to `rotate_bkup` in the same directory as the image
- If `rotate_bkup` cannot be created (e.g., on read-only network shares), falls back to `~/rotate_bkup`
- Duplicate backups get unique names: `image_1.jpg`, `image_2.jpg`, etc.

## Supported Formats

- JPEG (`.jpg`, `.jpeg`) - case-insensitive
- PNG (`.png`)

## Error Handling & Safety

- **Automatic temp file cleanup** - no orphaned files on errors
- **Backup verification** - ensures backups succeed before replacing originals
- **Permission checks** - validates write access before operations
- **File validation** - verifies output files are not empty or corrupted
- **Fallback backup location** - uses `~/rotate_bkup` if local directory isn't writable
- **Timeout protection** - won't hang if Finder is unresponsive

## Performance Optimizations

- Backup directory caching (avoids repeated filesystem checks)
- Fast file copying (optimized for network shares)
- Efficient path operations
- Temp files created on same filesystem for atomic operations

## Installation

### Quick Install (One-liner)

```bash
curl -o rotate.py https://raw.githubusercontent.com/kereilly58/rotate-jpeg/main/rotate.py && chmod +x rotate.py
```

### Full Installation

1. Clone this repository:
```bash
git clone https://github.com/kereilly58/rotate-jpeg.git
cd rotate-jpeg
```

2. Make executable:
```bash
chmod +x rotate.py
```

3. Optionally, create a symlink for easier access:
```bash
sudo ln -s $(pwd)/rotate.py /usr/local/bin/rotate
```

Then you can use it from anywhere:
```bash
rotate photo.jpg r
rotate -p
```

## Credits

Created by Keith Reilly with assistance from Claude (Anthropic).

## License

Free to use and modify.
