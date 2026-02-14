# Quick Start

## Your happiness paper is now a mind map 🧠

I turned your LaTeX research into something you can actually navigate without getting lost.

### What you've got:

**📄 Your original stuff:**
- `examples/happiness.tex` - Your happiness research (untouched)

**🗺️ The mind map versions:**
- `outputs/happiness_mindmap.md` - Markdown version for Markmap
- `outputs/happiness_mindmap.html` - **The good stuff** (open this in your browser!)

### Try these commands:

```bash
# Open the interactive version
open outputs/happiness_mindmap.html

# Make a new version with shorter text chunks
./run.sh examples/happiness.tex --markmap-mode --truncate-at 30 --output outputs/happiness_short.md

# Convert something else
./run.sh examples/sample_paper.tex --markmap-mode --output outputs/math_stuff.md
```

### What you'll see:

Your happiness research now looks like this:

```
# Happiness Research
├── Core equation (Happiness = Reality - Expectations)
├── Baseline happiness (℘ parameter)
│   └── 📊 Click to see the genetics/temperament details
├── How expectations work (age-based model)
├── The desire problem (Buddhist perspective)
└── Why people react differently
    ├── Sensitivity factors 
    └── Social comparison effects
```

### The cool bits:

- **📖 Expandable sections** - Long explanations hide behind "📊 Explanation" buttons
- **🧮 Math that actually works** - Your equations render properly
- **🌳 Zoom and navigate** - Click around, zoom in/out, collapse sections
- **🎨 Actually usable** - No more scrolling through 50 pages linearly

### Quick tips:
- The `.html` file is where the magic happens - open it first
- Play with `--truncate-at` to control how much text shows before the expand button
- Math equations never get truncated (because that would be stupid)
- If something looks weird, try regenerating with different settings

---

*Made by someone who got tired of reading academic papers the old way*