#!/usr/bin/env python3
"""
Post-process Markmap HTML files to add expand/collapse controls
"""

import sys
from pathlib import Path

def add_controls_to_html(html_file_path):
    """Add expand/collapse controls to a Markmap HTML file."""
    
    controls_html = '''
<!-- Markmap Controls -->
<div id="markmap-controls" style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: white; padding: 8px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: sans-serif;">
  <button onclick="fitMap()" style="margin: 2px; padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px; background: #f9f9f9; cursor: pointer; font-size: 12px;">📐 Fit</button>
  <button onclick="expandAll()" style="margin: 2px; padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px; background: #f9f9f9; cursor: pointer; font-size: 12px;">📂 Expand All</button>
  <button onclick="collapseAll()" style="margin: 2px; padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px; background: #f9f9f9; cursor: pointer; font-size: 12px;">📁 Collapse All</button>
</div>

<script>
// Wait for page to load
setTimeout(() => {
  window.fitMap = function() {
    if (window.mm && window.mm.fit) {
      window.mm.fit();
    }
  };
  
  window.expandAll = function() {
    // Simply open all <details> elements
    const allDetails = document.querySelectorAll('details');
    allDetails.forEach(detail => {
      detail.open = true;
    });
    console.log(`Expanded ${allDetails.length} details elements`);
  };
  
  window.collapseAll = function() {
    // Simply close all <details> elements
    const allDetails = document.querySelectorAll('details');
    allDetails.forEach(detail => {
      detail.open = false;
    });
    console.log(`Collapsed ${allDetails.length} details elements`);
  };
}, 1000);
</script>
'''
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Insert controls before </body>
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', controls_html + '\n</body>')
        else:
            # Fallback - append to end
            html_content += controls_html
        
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Added expand/collapse controls to {html_file_path}")
        
    except Exception as e:
        print(f"❌ Error adding controls to {html_file_path}: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_markmap_controls.py <html_file>")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    if not html_file.exists():
        print(f"Error: File {html_file} does not exist")
        sys.exit(1)
    
    add_controls_to_html(html_file)