# Rotate JPEG

A simple command-line tool to rotate JPEG images losslessly using EXIF orientation data.

## Features

- Lossless rotation using EXIF orientation
- Simple command-line interface
- Three rotation options: left (90° CCW), right (90° CW), and flip (180°)

## Requirements

- Python 3
- Pillow library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/rotate-jpeg.git
cd rotate-jpeg
```

2. Install dependencies:
```bash
pip3 install Pillow
```

3. Install the command globally:
```bash
sudo cp rotate_jpeg.py /usr/local/bin/rotate
sudo chmod +x /usr/local/bin/rotate
```

## Usage

```bash
rotate <jpeg_file> <direction>
```

**Directions:**
- `l` - Rotate 90° left (counter-clockwise)
- `r` - Rotate 90° right (clockwise)
- `f` - Flip 180°

**Examples:**
```bash
rotate photo.jpg r    # Rotate right 90°
rotate photo.jpg l    # Rotate left 90°
rotate photo.jpg f    # Flip 180°
```

## License

Free to use and modify.
