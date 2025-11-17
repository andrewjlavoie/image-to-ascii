# ASCII Background Generator

Convert images to colorful ASCII art for backgrounds, terminals, and more.

## Features

- **Multiple Output Formats**: Terminal (ANSI colors), image files (PNG/JPG), and JSON (for LLM processing)
- **Rich Color Modes**: Black & white, source colors, rainbow, gradients, and solid colors
- **Smart Resolution**: Auto-detects source image size, or specify exact output dimensions for wallpapers
- **Flexible Scaling**: Scale by percentage (e.g., `--scale=0.1` for 10% size)
- **Wallpaper Creation**: `--output-resolution=4k` creates exact 4K pixel output (not huge character grids!)
- **Custom Character Sets**: Use any characters you want (e.g., `--custom-chars " !@?"`)
- **Image Effects**: Brightness, contrast, invert, aspect ratio correction
- **Customizable Borders**: Add decorative borders and padding
- **Extended Character Set**: Fine detail with comprehensive ASCII character mapping

## Quick Start: 10 Wallpaper Workflows

### 1. Standard 4K Monitor Wallpaper
```bash
ascii-bg photo.jpg --output-resolution=4k --color-mode=source -o wallpaper.png
```
Creates a 3840×2160px wallpaper preserving original image colors (~8 MB).

### 2. 1080p HD Wallpaper
```bash
ascii-bg image.jpg --output-resolution=1080p --color-mode=source -o desktop.png
```
Perfect for 1920×1080 displays (~2 MB).

### 3. Ultrawide Monitor (21:9)
```bash
ascii-bg landscape.jpg --output-resolution=3440x1440 --color-mode=source -o ultrawide.png
```
Custom resolution for 21:9 ultrawide displays (~5 MB).

### 4. Dual Monitor Setup (Side by Side)
```bash
ascii-bg wide-photo.jpg --output-resolution=3840x1080 --color-mode=source -o dual-monitor.png
```
Spans two 1080p monitors horizontally (~4 MB).

### 5. Rainbow Gradient 4K
```bash
ascii-bg photo.jpg --output-resolution=4k --color-mode=rainbow \
  --gradient-direction=diagonal -o rainbow-wall.png
```
Vibrant rainbow diagonal gradient over ASCII art (~8 MB).

### 6. Custom Color Gradient
```bash
ascii-bg sunset.jpg --output-resolution=4k --color-mode=gradient \
  --gradient-colors=#FF6B35,#F7931E,#FDC830 --gradient-direction=vertical -o sunset-wall.png
```
Warm sunset-themed gradient (~8 MB).

### 7. Minimalist High Contrast
```bash
ascii-bg portrait.jpg --output-resolution=1080p --custom-chars " .:-=#@" \
  --contrast=50 --brightness=10 -o minimal.png
```
Clean, high-contrast minimalist aesthetic (~2 MB).

### 8. Retro Computer Style
```bash
ascii-bg retro-pic.jpg --output-resolution=1080p --color-mode=solid \
  --text-color=green --bg-color=black --charset=simple -o retro.png
```
Classic green-on-black terminal look (~1 MB).

### 9. Compact File Size 4K
```bash
ascii-bg image.jpg --output-resolution=4k --font-size=8 \
  --color-mode=source -o compact-4k.png
```
4K resolution with smaller font for reduced file size (~5 MB).

### 10. Mobile Wallpaper (Portrait)
```bash
ascii-bg photo.jpg --output-resolution=1080x1920 --color-mode=source -o mobile.png
```
Portrait orientation for smartphones (~3 MB).

### Pro Tips:
- **Always use `--output-resolution`** for wallpapers (not `-r`)
- **Add `--color-mode=source`** to preserve original photo colors
- **Adjust `--font-size`** to control detail level and file size
- **Use `--brightness` and `--contrast`** to fine-tune the look

## Installation

Using UV (recommended):
```bash
uv pip install ascii-bg
```

Or with pip:
```bash
pip install ascii-bg
```

## Development Setup

This project uses UV for dependency management and virtual environments:

```bash
# Clone the repository
git clone <repo-url>
cd ascii-background-generator

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Basic usage - display in terminal (uses source image resolution)
ascii-bg image.jpg

# Scale down large images for viewing
ascii-bg large-image.jpg --scale=0.1

# Create 4K wallpaper (output is exactly 3840×2160 pixels)
ascii-bg photo.png --output-resolution=4k -o wallpaper.png

# Custom character sets
ascii-bg image.jpg --custom-chars " .!@#" -o output.png

# Rainbow colors with scaling
ascii-bg image.jpg --scale=0.2 --color-mode=rainbow -o rainbow.png

# Custom gradient
ascii-bg input.jpg --color-mode=gradient --gradient-colors=#FF0000,#0000FF,#00FF00

# JSON output for LLM processing
ascii-bg image.jpg -o output.json
```

### API

```python
from ascii_bg.core import AsciiConverter

# Create converter
converter = AsciiConverter(
    resolution=(1920, 1080),
    color_mode="rainbow",
    brightness=10,
    border="double"
)

# Convert image
result = converter.convert("input.jpg")

# Output options
result.display_terminal()          # ANSI terminal output
result.save_image("output.png")   # Rendered image
result.save_json("output.json")   # For LLM processing
```

## Common Use Cases

### Creating Wallpapers

```bash
# 4K monitor wallpaper (3840×2160 pixels, ~8 MB)
ascii-bg photo.jpg --output-resolution=4k -o wallpaper.png

# 1080p wallpaper with source colors
ascii-bg image.jpg --output-resolution=1080p --color-mode=source -o bg.png

# Custom size with rainbow gradient
ascii-bg photo.png --output-resolution=2560x1440 --color-mode=rainbow -o wall.png
```

### Terminal Viewing

```bash
# Auto-size to source (may be too large)
ascii-bg image.jpg

# Scale down for better viewing (recommended)
ascii-bg large-image.jpg --scale=0.1

# Tiny preview (5% of original)
ascii-bg huge-photo.png --scale=0.05
```

### Custom Artistic Effects

```bash
# Only use exclamation marks and at symbols
ascii-bg photo.jpg --custom-chars " !@" -o minimalist.png

# Circles gradient
ascii-bg image.jpg --custom-chars " .oO@" --scale=0.2 -o circles.png

# Numbers only
ascii-bg photo.png --custom-chars " 123456789" -o numbers.png
```

### Important Tips

**For Wallpapers:**
- ✓ Use `--output-resolution=4k` (creates 3840×2160 px, ~8 MB)
- ✗ Don't use `-r 4k` alone (creates 4k character grid, ~600 MB!)

**For Terminal:**
- ✓ Use `--scale=0.1` for large images
- Default (source resolution) works great for small images

**For File Sizes:**
- Small files: `--scale=0.1 --font-size=8`
- Quality output: `--output-resolution=4k --font-size=10`

## CLI Options

```
ascii-bg <image> [options]

Resolution & Scaling:
  -r, --resolution         Character grid: 4k, 1080p, or WxH (default: source image size)
  --output-resolution      Output pixels for wallpapers: 4k, 1080p, or WxH
  --scale                  Scale by percentage: 0.5 (50%), 0.1 (10%), etc.

Character Sets:
  --charset                Preset: simple, extended, block, minimal (default: extended)
  --custom-chars           Custom characters from light to dark (e.g., " .!@#")

Color Options:
  --color-mode             black-white, source, rainbow, gradient, solid
  --bg-color               Background color for solid mode
  --text-color             Text color for solid mode
  --gradient-colors        Comma-separated colors for gradient
  --gradient-direction     horizontal, vertical, diagonal

Effects:
  --brightness             -100 to 100 (default: 0)
  --contrast               -100 to 100 (default: 0)
  --invert                 Invert character density
  --no-aspect-correct      Disable aspect ratio correction

Border/Padding:
  --border                 none, simple (default: none)
  --border-char            Custom border character (default: #)
  --padding                0-10 (default: 0)

Output:
  -o, --output             Output file (PNG, JPG, JSON, or TXT)
  --terminal               Display in terminal (default: enabled)
  --font-size              Font size for image output: 4-72 (default: 10)
  --font-family            Font family (default: DejaVuSansMono)
```

## Development

### Code Quality

This project uses ruff for linting/formatting and pyright for type checking:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

### Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=ascii_bg --cov-report=html
```

### Git Workflow

We use feature branching with PR-based QA:

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "Description of changes"

# Push and create PR
git push -u origin feature/your-feature-name
```

All PRs automatically run ruff and pyright checks via GitHub Actions.

## Architecture

```
ascii_bg/
├── core/                    # Core API library
│   ├── converter.py         # Main ASCII conversion engine
│   ├── image_processor.py   # Image loading and preprocessing
│   ├── color_handler.py     # Color mode implementations
│   ├── character_sets.py    # ASCII character definitions
│   ├── renderer.py          # Output rendering
│   └── effects.py           # Image effects and transformations
└── cli.py                   # CLI entry point
```

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass and code quality checks succeed
5. Submit a pull request
