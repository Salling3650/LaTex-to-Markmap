# Copilot Instructions for LaTeX to Mind Map Converter

## Overview
This project converts LaTeX documents into hierarchical mind map structures compatible with Markmap, Obsidian, Xmind, EdrawMind, and other tools. It uses Python with `pylatexenc` for parsing and regex fallbacks for robustness.

## Build, Test, and Lint Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Tool
```bash
# Via convenience script (requires venv)
./run.sh examples/sample_paper.tex --markmap-mode --output outputs/output.md

# Direct Python
python3 latex_to_mindmap.py paper.tex --format markdown --output mindmap.md

# Common examples
python3 latex_to_mindmap.py paper.tex --format json --output mindmap.json
python3 latex_to_mindmap.py paper.tex --markmap-mode --truncate-at 50 --output mindmap.md
```

### No existing test suite
The codebase currently has no automated tests. If adding tests, follow these conventions:
- Test files should go in a `tests/` directory at root level
- Use standard Python testing (unittest or pytest recommended)
- Test the two main pathways: `pylatexenc`-based parsing and regex fallback

### Linting
No linter is currently configured. If adding one, prefer tools compatible with Python 3.10+.

## Architecture

### Core Components

**1. MindMapNode** (dataclass)
- Represents a single node in the hierarchical tree
- Fields: `title`, `content`, `node_type`, `children`, `level`
- Methods: `add_child()`, `to_dict()` for serialization

**2. LatexParser**
- Main parsing engine that converts LaTeX to MindMapNode trees
- Constructor takes LaTeX file path and optional base directory for includes
- Key methods:
  - `parse()` - Entry point, handles document structure extraction
  - `_parse_with_pylatexenc()` - Uses pylatexenc library for robust AST parsing
  - `_parse_with_regex_fallback()` - Fallback when pylatexenc unavailable
  - `_process_pylatexenc_node()` - Recursively processes AST nodes
  - `_handle_macro_node()` - Processes LaTeX commands (sections, theorems, etc.)
  - `_handle_environment_node()` - Processes environments (equation, proof, etc.)
  - `_clean_latex_text()` - Strips LaTeX markup while preserving math expressions

**3. MindMapFormatter**
- Converts MindMapNode trees to output formats
- Methods:
  - `to_markdown()` - Generates markdown with optional Markmap optimizations
  - `to_json()` - Generates JSON representation for programmatic use
- Markmap mode adds `<details>` elements with truncation at `--truncate-at` characters

**4. add_markmap_controls.py** (helper script)
- Post-processes HTML output to inject expand/collapse buttons
- Used when generating interactive Markmap visualizations
- Not automatically called; must be invoked separately if needed

### Parsing Strategy

**Primary Path (with pylatexenc):**
1. Load LaTeX file and resolve `\input{}`/`\include{}` includes
2. Extract document preamble for title
3. Use LatexWalker to build AST of document content
4. Recursively traverse AST, mapping LaTeX constructs to mind map nodes:
   - Sections (`\section`, `\subsection`, etc.) → hierarchy levels
   - Theorem-like environments → labeled child nodes
   - Math environments → preserved as-is
   - Lists → flattened to structured children

**Fallback Path (regex-based):**
- Used when pylatexenc import fails (non-critical dependency)
- Extracts structure via regex patterns for sections, theorems, lists
- Less robust but covers most common academic papers (~70% coverage)

### Key Conventions

**1. LaTeX Command Support**
- Supported: `\section{...}`, `\subsection{...}`, `\subsubsection{...}`, `\chapter{...}`, `\part{...}`, `\paragraph{...}`, `\subparagraph{...}`
- Supported environments: `theorem`, `definition`, `lemma`, `proposition`, `proof`, `example`, `remark`, `equation`, `equation*`, `align`, `align*`, `itemize`, `enumerate`
- Math expressions are always preserved: `$...$`, `\(...\)`, `$$...$$`
- Custom macros are NOT expanded; they're stripped as unknown commands

**2. Node Types**
- `"section"` - Standard section
- `"definition"`, `"theorem"`, `"lemma"`, `"proof"`, etc. - Theorem-like environments
- `"equation"` - Math equations
- `"list_item"` - List item
- Any others created dynamically from environment names

**3. Text Cleaning**
- Math expressions are protected during LaTeX cleanup (regex placeholder mechanism)
- Commands like `\textbf{text}` become `text`
- Braces are removed: `{text}` → `text`
- Line breaks (`\\`) are converted to spaces
- Multiple spaces collapsed to single space

**4. Markmap Mode Optimizations**
- Long text is wrapped in `<details><summary>📊 Explanation</summary>` elements
- Truncation threshold controlled by `--truncate-at` parameter (default: 100 chars)
- Math and short content are never truncated
- Generates `.md` files that can be converted to interactive HTML by Markmap

## MCP Servers

### Playwright Browser Automation
For testing HTML output and interactive Markmap features:
```bash
# Install Playwright (if implementing HTML tests)
pip install playwright
playwright install

# Usage in tests:
# - Verify HTML structure of generated mind maps
# - Test expand/collapse button functionality
# - Validate math rendering in Markmap
```

## Important Notes

- **Graceful degradation:** Parser always succeeds, falling back to simpler approaches
- **Math preservation:** All math notation is protected and never modified during text cleanup
- **Virtual environment required:** The `run.sh` script expects `.venv` to exist and contain installed dependencies
- **No external tools:** Conversion happens in-process; no external LaTeX/PDF tools needed
- **Include resolution:** `\input{}` and `\include{}` are resolved relative to the input file's directory
