# Quick Usage Guide

## Setup (One-time)

```bash
cd /path/to/this/program
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install -g markmap-cli  # For HTML output
```

## Usage

All commands follow this format:

```bash
python3 latex_to_mindmap.py YOUR_LATEX_FILE --format FORMAT --output OUTPUT_FILE
```

### Markdown (plain text structure)
```bash
python3 latex_to_mindmap.py /path/to/paper.tex --format markdown --output mindmap.md
cat mindmap.md
```

### JSON (for programmatic use)
```bash
python3 latex_to_mindmap.py /path/to/paper.tex --format json --output mindmap.json
```

### Markmap (interactive HTML - recommended!)
```bash
python3 latex_to_mindmap.py /path/to/paper.tex --format markdown --markmap-mode --output mindmap.md
markmap mindmap.md --output mindmap.html
open mindmap.html
```

## One-liner examples

**Markdown:**
```bash
./run.sh /path/to/paper.tex --output /tmp/mindmap.md && cat /tmp/mindmap.md
```

**Interactive HTML (best):**
```bash
./run.sh /path/to/paper.tex --markmap-mode --output /tmp/mindmap.md && markmap /tmp/mindmap.md --output /tmp/mindmap.html && open /tmp/mindmap.html
```

## Tips

- `--markmap-mode` creates expandable sections (best for long texts)
- `--truncate-at 50` controls when text gets hidden in expandable menus (default: 100 chars)
- Math equations are preserved and render correctly in HTML
- All explanatory text stays in the hierarchy (not lost!)

## Example on your own file

```bash
# Navigate to the program
cd /Users/frederiksallinghansen/Desktop/projects/Programming/1_Work_in_progress/LaTeX_mindmap/latex\ to\ mindmap
source .venv/bin/activate

# Convert your file
./run.sh /path/to/your/file.tex --markmap-mode --output /tmp/mymap.md

# View it
markmap /tmp/mymap.md --output /tmp/mymap.html
open /tmp/mymap.html
```

Done! Your LaTeX paper is now an interactive mind map.
