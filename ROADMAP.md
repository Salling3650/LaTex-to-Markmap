# LaTeX to Mind Map Converter - Roadmap

## Planned Features

### List Processing
- [ ] **Support numbered lists with proper formatting** - Currently lists with numbers aren't handled correctly
- [ ] **Consolidate list items in single nodes** - Both `enumerate` and `itemize` environments should be grouped as one node instead of separate entries
- [ ] **Display lists in details panels** - Ensure list content is properly visible in expandable sections

### Mathematical Content
- [ ] **Fix inline math rendering** - Resolve issue where inline math (e.g., `$5+5=10$`) displays with visible delimiters
- [ ] **Improve equation handling** - Better support for complex mathematical expressions

### Graphics & Figures
- [ ] **Display images and figures** - Render embedded TikZ graphics, pgfplots, and included images
- [ ] **Support figure environments** - Properly extract and display content from `\begin{figure}...\end{figure}`
- [ ] **Handle graphics captions** - Extract and display `\caption` text with graphics

### Document Metadata
- [ ] **Use document title from LaTeX** - Extract and display the actual project title instead of generic "LaTeX Document"
- [ ] **Support `\title` and `\author` commands** - Parse document metadata from preamble

### References & Citations
- [ ] **Support footnotes** - Extract and display `\footnote{}` content
- [ ] **BibTeX integration** - Display citations with author/title information from `.bib` files
- [ ] **Handle `\ref` and `\label`** - Support cross-references and labeled equations/figures

## Priority

### High Priority (Core Functionality)
1. List consolidation and proper formatting
2. Inline math delimiter fix
3. Document title extraction
4. Graphics/figure display support

### Medium Priority (Common Features)
1. BibTeX citation handling
2. Cross-reference support (`\ref`, `\label`)
3. Footnotes

### Lower Priority (Advanced)
1. Complex equation environments
2. Advanced graphics package support (asymptote, metapost)
3. Table formatting optimization

## Notes

- The converter currently uses regex-based parsing which handles most LaTeX well
- Graphics support via TikZ compilation is technically feasible but complex
- BibTeX integration requires parsing `.bib` files and matching citations
- Focus on most commonly used features first (lists, math, titles)
