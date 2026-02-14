# LaTeX to Mind Map Converter

Got a huge LaTeX paper? Turn it into an interactive mind map that you can actually navigate without losing your sanity.

## What it does

- Rips apart your LaTeX document and rebuilds it as a mind map
- Keeps all your precious math equations intact
- Works with Markmap, Obsidian, Xmind, and friends
- Handles the usual academic stuff: theorems, proofs, definitions, etc.
- Falls back gracefully when it hits weird LaTeX it doesn't understand

## Project Structure

```
latex-to-mindmap/
├── latex_to_mindmap.py      # Main converter script
├── run.sh                   # Convenient run script  
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── examples/               # Sample LaTeX documents
│   ├── happiness.tex       # Your happiness research
│   └── sample_paper.tex    # Demo mathematical paper
├── outputs/                # Generated mind maps
│   ├── *.md               # Markdown outputs
│   ├── *.json             # JSON outputs  
│   └── *.html             # Interactive Markmap files
└── .venv/                 # Python virtual environment
```

## How to use it

First, install the dependencies:
```bash
pip install -r requirements.txt
```

Then just point it at your LaTeX file:

```bash
# Basic conversion
python latex_to_mindmap.py paper.tex

# Save to a file  
python latex_to_mindmap.py paper.tex --output mindmap.md

# Make it work nicely with Markmap
python latex_to_mindmap.py paper.tex --markmap-mode --output pretty_mindmap.md

# Spit out JSON instead
python latex_to_mindmap.py paper.tex --format json --output data.json
```

There's also a `run.sh` script if you're feeling lazy:
```bash
./run.sh examples/happiness.tex --markmap-mode
```

## What you get

### Markdown output
Perfect for Markmap or dropping into Obsidian:

```markdown
# Your Amazing Paper

- Introduction  
  - Why this matters
  - What we're trying to solve
- The Math Stuff
  - Important Theorem: If $x > 0$ then...
  - 📊 Explanation: This actually means...
  - Proof: Well, obviously...
```

### JSON output  
For when you want to build your own visualization:

```json
{
  "title": "Your Amazing Paper",
  "type": "document", 
  "children": [
    {
      "title": "Introduction",
      "type": "section",
      "children": [...]
    }
  ]
}
```

## LaTeX stuff it understands

### Document structure
- Sections, subsections, all that hierarchy stuff
- Chapters and parts if you're writing a book
- Paragraphs and subparagraphs

### Academic bits
- Theorems, definitions, lemmas, propositions
- Proofs (it'll try to keep them readable)
- Equations and math environments  
- Bulleted and numbered lists
- Figure captions

### Math
- Inline math like $x = 2$ or \(complicated stuff\)
- Display equations $$like this$$
- Everything gets preserved so it renders properly

## Caveats

- Doesn't know about every LaTeX package ever made (covers maybe 70% of typical academic papers)
- Won't expand your custom macros
- Tables are tricky and might not come out great
- Some exotic LaTeX features will be ignored

But hey, it beats manually copying and pasting your entire paper into a mind mapping tool.

## Getting it into your mind mapping tool

### Markmap
1. Save as `.md` file
2. Open with Markmap (online or VS Code extension)  
3. Enjoy your interactive mind map

### Obsidian
1. Drop the `.md` file into your vault
2. Enable MathJax in settings if you want pretty math
3. Use graph view to see connections

### Xmind/EdrawMind  
1. Copy-paste the markdown structure
2. Or use the JSON output with a custom importer if you're feeling ambitious

### Freeplane
1. Find a markdown-to-Freeplane converter
2. Or just use the hierarchy as a guide for manual entry

## Requirements

You need Python 3.10+ and:
```bash
pip install pylatexenc
```

If you don't have `pylatexenc`, it'll fall back to regex parsing (which works but isn't as smart).

---

This tool exists because reading 50-page LaTeX papers linearly is medieval torture. Use it, improve it, or complain about it - whatever works for you.