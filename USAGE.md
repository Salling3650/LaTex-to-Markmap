# Quick Usage Guide

## Setup (One-time)

### Option 1: Without virtual environment (simplest)
```bash
pip install -r requirements.txt
npm install -g markmap-cli  # For HTML output
```

### Option 2: With virtual environment (recommended for projects)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install -g markmap-cli
```

## Basic Usage

All commands follow this format:

```bash
python3 latex_to_mindmap.py YOUR_LATEX_FILE --format FORMAT --output OUTPUT_FILE
```

**Outputs go to `outputs/` by default** if you don't specify `--output`

## Examples

### Markdown (plain text structure)
```bash
python3 latex_to_mindmap.py paper.tex
# Saves to: outputs/paper.md
```

### JSON (for programmatic use)
```bash
python3 latex_to_mindmap.py paper.tex --format json
# Saves to: outputs/paper.json
```

### Markmap (interactive HTML - recommended!)
```bash
python3 latex_to_mindmap.py paper.tex --markmap-mode
markmap outputs/paper.md --output outputs/paper.html
open outputs/paper.html
```

## One-liner: Convert and view

**Interactive HTML (best):**
```bash
./run.sh paper.tex --markmap-mode && markmap outputs/paper.md --output outputs/paper.html && open outputs/paper.html
```

**Markdown to stdout:**
```bash
./run.sh paper.tex
```

## Tips

- `--markmap-mode` creates expandable sections (best for long texts)
- `--truncate-at 50` controls when text gets hidden (default: 100 chars)
- Math equations are preserved and render correctly in HTML
- All explanatory text stays in the hierarchy

---

Done! Your LaTeX paper is now an interactive mind map.
