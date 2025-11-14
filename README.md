# ASCII Background Generator

Convert images to colorful ASCII art for backgrounds, terminals, and more.

## Features

- **Multiple Output Formats**: Terminal (ANSI colors), image files (PNG/JPG), and JSON (for LLM processing)
- **Rich Color Modes**: Black & white, source colors, rainbow, gradients, and solid colors
- **Resolution Presets**: Quick shortcuts like `4k`, `1080p`, or custom dimensions
- **Image Effects**: Brightness, contrast, invert, aspect ratio correction
- **Customizable Borders**: Add decorative borders and padding
- **Extended Character Set**: Fine detail with comprehensive ASCII character mapping

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
# Basic usage - display in terminal
ascii-bg image.jpg

# 4K resolution with rainbow colors
ascii-bg image.jpg --resolution=4k --color-mode=rainbow

# Save as image file
ascii-bg photo.png -r 1920x1080 --brightness=20 -o output.png

# Custom gradient
ascii-bg input.jpg --color-mode=gradient --gradient-colors=#FF0000,#0000FF,#00FF00

# JSON output for LLM processing
ascii-bg image.jpg --json -o output.json
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

## CLI Options

```
ascii-bg <image> [options]

Resolution:
  -r, --resolution      4k, 1080p, 720p, or custom WxH (default: 1920x1080)

Color Options:
  --color-mode          black-white, source, rainbow, gradient, solid
  --bg-color           Background color for solid mode
  --text-color         Text color for solid mode
  --gradient-colors    Comma-separated colors for gradient
  --gradient-direction horizontal, vertical, diagonal

Effects:
  --brightness         -100 to 100 (default: 0)
  --contrast           -100 to 100 (default: 0)
  --invert             Invert character density
  --no-aspect-correct  Disable aspect ratio correction

Border/Padding:
  --border             none, simple, double, custom
  --border-char        Custom border character
  --padding            0-10 (default: 0)

Output:
  -o, --output         Output file (PNG, JPG, or JSON)
  --terminal           Display in terminal
  --json               JSON format for LLM processing
  --font-size          Font size for image output (default: 10)
  --font-family        Font family (default: Courier)
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
