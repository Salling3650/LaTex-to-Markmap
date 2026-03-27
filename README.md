# LaTeX to Mind Map Converter

Got a huge LaTeX paper? Turn it into an interactive mind map that you can actually navigate without losing your sanity.

## What it does

- Rips apart your LaTeX document and rebuilds it as a mind map
- Keeps all your precious math equations intact
- Works with Markmap, Obsidian, Xmind, and friends
- Handles the usual academic stuff: theorems, proofs, definitions, etc.
- Falls back gracefully when it hits weird LaTeX it doesn't understand

## Quick Start

### Installation
```bash
pip install -r requirements.txt
npm install -g markmap-cli  # For HTML output
```

### Simple usage
```bash
# Convert to markdown (saves to outputs/ by default)
python3 latex_to_mindmap.py paper.tex

# Interactive HTML (best!)
python3 latex_to_mindmap.py paper.tex --markmap-mode
markmap outputs/paper.md --output outputs/paper.html
open outputs/paper.html

# JSON output
python3 latex_to_mindmap.py paper.tex --format json
```

See [USAGE.md](USAGE.md) for detailed examples and more options.

## How it works

The converter:
1. Parses your LaTeX file (including `\input` and `\include` directives)
2. Extracts document structure (sections, subsections, paragraphs)
3. Captures all text content, equations, theorems, and lists
4. Builds a hierarchical tree that can be exported as:
   - **Markdown** - for Markmap or Obsidian
   - **JSON** - for custom tools

## What it captures

- **Document structure**: Sections, subsections, chapters, paragraphs
- **Academic content**: Theorems, definitions, lemmas, proofs, examples
- **Math**: Inline (`$...$`, `\(...\)`) and display (`$$...$$`, `\[...\]`) equations
- **Text**: All explanatory text, descriptions, and content
- **Lists**: Itemize and enumerate environments

## Limitations

- Doesn't expand custom LaTeX macros (they're stripped as unknown commands)
- Tables aren't specially handled (may not render well)
- Some exotic LaTeX features will be ignored
- Coverage: ~70% of typical academic papers

---

This tool exists because reading 50-page LaTeX papers linearly is medieval torture. Use it, improve it, or complain about it - whatever works for you.
