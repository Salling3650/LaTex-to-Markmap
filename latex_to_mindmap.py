#!/usr/bin/env python3
"""
LaTeX to Mind Map Converter

Converts LaTeX documents into hierarchical mind-map structures suitable for
import into tools like Xmind, EdrawMind, Markmap, Freeplane, or Obsidian.

Usage:
    python latex_to_mindmap.py document.tex --format markdown --output mindmap.md
    python latex_to_mindmap.py paper.tex --format json --output mindmap.json

Author: AI Assistant
"""

import argparse
import json
import re
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from pylatexenc.latexwalker import (
        LatexWalker, 
        LatexMacroNode, 
        LatexEnvironmentNode, 
        LatexCharsNode, 
        LatexMathNode,
        LatexGroupNode
    )
    PYLATEXENC_AVAILABLE = True
except ImportError:
    PYLATEXENC_AVAILABLE = False
    warnings.warn("pylatexenc not available. Install with: pip install pylatexenc")
    # Define dummy types for type hints when pylatexenc is not available
    class LatexMacroNode: pass
    class LatexEnvironmentNode: pass
    class LatexCharsNode: pass
    class LatexMathNode: pass
    class LatexGroupNode: pass


@dataclass
class MindMapNode:
    """Represents a node in the mind map tree structure."""
    title: str
    content: str = ""
    node_type: str = "section"
    children: List['MindMapNode'] = field(default_factory=list)
    level: int = 0
    
    def add_child(self, child: 'MindMapNode') -> None:
        """Add a child node."""
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'content': self.content,
            'type': self.node_type,
            'level': self.level,
            'children': [child.to_dict() for child in self.children]
        }


class LatexParser:
    """Parses LaTeX documents using pylatexenc or fallback regex patterns."""
    
    # Sectioning commands in order of hierarchy
    SECTION_LEVELS = {
        'part': 0,
        'chapter': 1,
        'section': 2,
        'subsection': 3,
        'subsubsection': 4,
        'paragraph': 5,
        'subparagraph': 6
    }
    
    # Common theorem-like environments
    THEOREM_ENVS = {
        'theorem', 'lemma', 'proposition', 'corollary', 'definition',
        'example', 'remark', 'note', 'proof', 'claim', 'fact'
    }
    
    def __init__(self, tex_content: str):
        self.tex_content = tex_content
        self.current_level = 2  # Start at section level
        
    def parse(self) -> MindMapNode:
        """Main parsing method. Returns root mind map node."""
        # Extract document body (remove preamble)
        body = self._extract_document_body()
        
        # Create root node
        title = self._extract_document_title() or "LaTeX Document"
        root = MindMapNode(title=title, node_type="document", level=0)
        
        if PYLATEXENC_AVAILABLE:
            # Force use of regex fallback for better structure
            root = self._parse_with_regex_fallback(body, root)
        else:
            root = self._parse_with_regex_fallback(body, root)
            
        return root
    
    def _extract_document_body(self) -> str:
        """Extract content between \\begin{document} and \\end{document}."""
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', 
                         self.tex_content, re.DOTALL)
        if match:
            return match.group(1)
        else:
            # If no document environment found, assume the entire content is the body
            # but remove common preamble elements
            content = self.tex_content
            # Remove documentclass, usepackage, title, author, date commands
            content = re.sub(r'\\documentclass.*?\n', '', content)
            content = re.sub(r'\\usepackage.*?\n', '', content)
            content = re.sub(r'\\title\{.*?\}\n?', '', content, flags=re.DOTALL)
            content = re.sub(r'\\author\{.*?\}\n?', '', content, flags=re.DOTALL)
            content = re.sub(r'\\date\{.*?\}\n?', '', content, flags=re.DOTALL)
            content = re.sub(r'\\maketitle\n?', '', content)
            content = re.sub(r'\\newtheorem.*?\n', '', content)
            return content.strip()
    
    def _extract_document_title(self) -> Optional[str]:
        """Extract document title from \\title command."""
        match = re.search(r'\\title\{([^}]+)\}', self.tex_content)
        if match:
            return self._clean_latex_text(match.group(1))
        
        # If no title found, try to extract from first section/subsection
        first_section = re.search(r'\\(?:sub)*section\{([^}]+)\}', self.tex_content)
        if first_section:
            return self._clean_latex_text(first_section.group(1))
        
        return None
    
    def _parse_with_pylatexenc(self, content: str, root: MindMapNode) -> MindMapNode:
        """Parse using pylatexenc library."""
        try:
            walker = LatexWalker(content)
            parsed_nodes = walker.get_latex_nodes()[0]
            
            current_section_nodes = {level: root for level in range(7)}
            
            for node in parsed_nodes:
                self._process_pylatexenc_node(node, current_section_nodes, root)
                
        except Exception as e:
            warnings.warn(f"pylatexenc parsing failed: {e}. Falling back to regex.")
            return self._parse_with_regex_fallback(content, root)
            
        return root
    
    def _process_pylatexenc_node(self, node: Any, section_nodes: Dict[int, MindMapNode], 
                                root: MindMapNode) -> None:
        """Process a single pylatexenc node."""
        if isinstance(node, LatexMacroNode):
            self._handle_macro_node(node, section_nodes)
        elif isinstance(node, LatexEnvironmentNode):
            self._handle_environment_node(node, section_nodes)
        elif isinstance(node, LatexMathNode):
            self._handle_math_node(node, section_nodes)
        elif hasattr(node, 'nodelist') and node.nodelist:
            # Recursively process nested nodes
            for child_node in node.nodelist:
                self._process_pylatexenc_node(child_node, section_nodes, root)
    
    def _handle_macro_node(self, node: LatexMacroNode, section_nodes: Dict[int, MindMapNode]) -> None:
        """Handle sectioning macros like \\section, \\subsection."""
        macro_name = node.macroname
        
        if macro_name in self.SECTION_LEVELS:
            level = self.SECTION_LEVELS[macro_name]
            
            # Extract section title
            title = ""
            if node.nodeargs and len(node.nodeargs) > 0:
                title_arg = node.nodeargs[0]
                if hasattr(title_arg, 'nodelist'):
                    title = self._nodes_to_text(title_arg.nodelist)
                else:
                    title = str(title_arg)
            
            title = self._clean_latex_text(title) or f"{macro_name.title()}"
            
            # Create new section node
            section_node = MindMapNode(
                title=title,
                node_type=macro_name,
                level=level
            )
            
            # Add to appropriate parent
            parent_level = level - 1
            while parent_level >= 0 and parent_level not in section_nodes:
                parent_level -= 1
            
            if parent_level >= 0:
                section_nodes[parent_level].add_child(section_node)
            
            # Update section tracking
            section_nodes[level] = section_node
            # Clear deeper levels
            for l in list(section_nodes.keys()):
                if l > level:
                    del section_nodes[l]
    
    def _handle_environment_node(self, node: LatexEnvironmentNode, 
                                section_nodes: Dict[int, MindMapNode]) -> None:
        """Handle environments like theorem, proof, itemize."""
        env_name = node.environmentname
        
        # Get current section to add content to
        current_section = section_nodes.get(max(section_nodes.keys()))
        if not current_section:
            return
        
        if env_name in self.THEOREM_ENVS:
            # Create theorem-like node
            title = f"{env_name.title()}"
            content = self._nodes_to_text(node.nodelist) if node.nodelist else ""
            content = self._clean_latex_text(content)
            
            # Special handling: if this is a definition and the current section has no content yet,
            # merge it into the section title instead of creating a separate child
            if env_name == 'definition' and not current_section.content and not current_section.children:
                current_section.content = content
                current_section.node_type = 'section_with_definition'
            else:
                theorem_node = MindMapNode(
                    title=title,
                    content=content,
                    node_type=env_name,
                    level=current_section.level + 1
                )
                current_section.add_child(theorem_node)
            
        elif env_name in ['itemize', 'enumerate']:
            # Handle lists
            self._handle_list_environment(node, current_section)
        elif env_name == 'equation':
            # Handle equations
            math_content = self._nodes_to_text(node.nodelist) if node.nodelist else ""
            equation_node = MindMapNode(
                title="Equation",
                content=f"$${math_content}$$",
                node_type="equation",
                level=current_section.level + 1
            )
            current_section.add_child(equation_node)
    
    def _handle_list_environment(self, node: LatexEnvironmentNode, parent: MindMapNode) -> None:
        """Handle itemize/enumerate environments."""
        list_node = MindMapNode(
            title=f"{node.environmentname.title()} List",
            node_type=node.environmentname,
            level=parent.level + 1
        )
        parent.add_child(list_node)
        
        # Extract items
        if node.nodelist:
            current_item = ""
            for child in node.nodelist:
                if isinstance(child, LatexMacroNode) and child.macroname == 'item':
                    if current_item.strip():
                        item_node = MindMapNode(
                            title=self._clean_latex_text(current_item)[:100] + "..." if len(current_item) > 100 else self._clean_latex_text(current_item),
                            content=self._clean_latex_text(current_item),
                            node_type="item",
                            level=list_node.level + 1
                        )
                        list_node.add_child(item_node)
                    current_item = ""
                else:
                    current_item += self._nodes_to_text([child])
            
            # Add last item
            if current_item.strip():
                item_node = MindMapNode(
                    title=self._clean_latex_text(current_item)[:100] + "..." if len(current_item) > 100 else self._clean_latex_text(current_item),
                    content=self._clean_latex_text(current_item),
                    node_type="item",
                    level=list_node.level + 1
                )
                list_node.add_child(item_node)
    
    def _handle_math_node(self, node: LatexMathNode, section_nodes: Dict[int, MindMapNode]) -> None:
        """Handle math mode nodes."""
        current_section = section_nodes.get(max(section_nodes.keys()))
        if not current_section:
            return
        
        math_content = self._nodes_to_text([node])
        if node.displaytype == 'display':
            math_content = f"$${math_content}$$"
        else:
            math_content = f"\\({math_content}\\)"
        
        math_node = MindMapNode(
            title="Math Expression",
            content=math_content,
            node_type="math",
            level=current_section.level + 1
        )
        current_section.add_child(math_node)
    
    def _nodes_to_text(self, nodes: List[Any]) -> str:
        """Convert list of nodes to text representation."""
        text = ""
        for node in nodes:
            if isinstance(node, LatexCharsNode):
                text += node.chars
            elif isinstance(node, LatexMathNode):
                text += node.latex_verbatim()
            elif hasattr(node, 'latex_verbatim'):
                text += node.latex_verbatim()
            elif hasattr(node, 'nodelist') and node.nodelist:
                text += self._nodes_to_text(node.nodelist)
        return text
    
    def _parse_with_regex_fallback(self, content: str, root: MindMapNode) -> MindMapNode:
        """Fallback parsing using regex patterns."""
        warnings.warn("Using regex fallback parser. Results may be less accurate.")
        
        # Split content by sections, but preserve the content between sections
        section_pattern = r'\\((?:sub)*(?:sub)*section)\{([^}]+)\}'
        matches = list(re.finditer(section_pattern, content))
        
        current_pos = 0
        section_stack = {0: root}
        
        for i, match in enumerate(matches):
            # Process content before this section (add to current section)
            if current_pos < match.start():
                pre_content = content[current_pos:match.start()].strip()
                if pre_content:
                    self._add_content_to_current_section(pre_content, section_stack)
            
            # Get content until next section (or end of document)
            next_match_start = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[match.end():next_match_start].strip()
            
            # Create section node
            section_type = match.group(1)
            section_title = self._clean_latex_text(match.group(2))
            level = self.SECTION_LEVELS.get(section_type, 2)
            
            # Extract main explanatory text (everything before first math/environment)
            main_text = self._extract_main_text(section_content)
            
            section_node = MindMapNode(
                title=section_title,
                content=main_text,
                node_type=section_type,
                level=level
            )
            
            # Find parent
            parent_level = level - 1
            while parent_level >= 0 and parent_level not in section_stack:
                parent_level -= 1
            
            if parent_level >= 0:
                section_stack[parent_level].add_child(section_node)
            
            section_stack[level] = section_node
            
            # Clear deeper levels
            for l in list(section_stack.keys()):
                if l > level:
                    del section_stack[l]
            
            # Process the remaining content in this section (equations, environments, etc.)
            remaining_content = self._extract_remaining_content(section_content)
            if remaining_content:
                self._add_structured_content_to_section(remaining_content, section_node)
            
            current_pos = next_match_start
        
        # Process remaining content after last section
        if current_pos < len(content):
            remaining_content = content[current_pos:].strip()
            if remaining_content:
                self._add_content_to_current_section(remaining_content, section_stack)
        
        return root
    
    def _extract_main_text(self, content: str) -> str:
        """Extract the main explanatory text before any math or environments."""
        # Find first math environment or equation
        math_patterns = [
            r'\\begin\{(align|equation|gather)\}',
            r'\\\[',
            r'\$\$',
            r'\\paragraph\{',
            r'\\begin\{(' + '|'.join(self.THEOREM_ENVS) + r')\}'
        ]
        
        first_math_pos = len(content)
        for pattern in math_patterns:
            match = re.search(pattern, content)
            if match and match.start() < first_math_pos:
                first_math_pos = match.start()
        
        main_text = content[:first_math_pos].strip()
        return self._clean_latex_text(main_text) if main_text else ""
    
    def _extract_remaining_content(self, content: str) -> str:
        """Extract content after the main text (math, environments, etc.)."""
        # Find first math environment or equation
        math_patterns = [
            r'\\begin\{(align|equation|gather)\}',
            r'\\\[',
            r'\$\$',
            r'\\paragraph\{',
            r'\\begin\{(' + '|'.join(self.THEOREM_ENVS) + r')\}'
        ]
        
        first_math_pos = len(content)
        for pattern in math_patterns:
            match = re.search(pattern, content)
            if match and match.start() < first_math_pos:
                first_math_pos = match.start()
        
        return content[first_math_pos:].strip() if first_math_pos < len(content) else ""
    
    def _add_structured_content_to_section(self, content: str, section_node: MindMapNode) -> None:
        """Add structured content (equations, theorems) to a section node."""
        # Find all structural elements with their positions
        all_elements = []
        
        # Find equations
        equation_patterns = [
            (r'\\begin\{(align|equation|gather)\}(.*?)\\end\{\1\}', 'equation'),
            (r'\\\[(.*?)\\\]', 'equation'),
            (r'\$\$(.*?)\$\$', 'equation')
        ]
        
        for pattern, element_type in equation_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                eq_content = match.group(2) if match.lastindex >= 2 else match.group(1)
                eq_content = eq_content.strip()
                if eq_content:
                    all_elements.append({
                        'type': element_type,
                        'content': eq_content,
                        'start': match.start(),
                        'end': match.end(),
                        'title': 'Key Equation'
                    })
        
        # Find theorem environments
        theorem_pattern = r'\\begin\{(' + '|'.join(self.THEOREM_ENVS) + r')\}(.*?)\\end\{\1\}'
        for match in re.finditer(theorem_pattern, content, re.DOTALL):
            env_name = match.group(1)
            env_content = self._clean_latex_text(match.group(2))
            all_elements.append({
                'type': 'theorem',
                'content': env_content,
                'start': match.start(),
                'end': match.end(),
                'title': f"{env_name.title()}"
            })
        
        # Find paragraphs
        paragraph_pattern = r'\\paragraph\{([^}]*)\}([^\\]*?)(?=\\|\Z)'
        for match in re.finditer(paragraph_pattern, content, re.DOTALL):
            para_title = self._clean_latex_text(match.group(1)) or "Note"
            para_content = self._clean_latex_text(match.group(2))
            if para_content:
                all_elements.append({
                    'type': 'paragraph',
                    'content': para_content,
                    'start': match.start(),
                    'end': match.end(),
                    'title': para_title
                })
        
        # Sort elements by position
        all_elements.sort(key=lambda x: x['start'])
        
        # Extract text between elements and pair with equations
        enhanced_elements = []
        last_end = 0
        
        for i, element in enumerate(all_elements):
            # Get text before this element
            if element['start'] > last_end:
                text_before = content[last_end:element['start']].strip()
                if text_before and not re.match(r'^\\[a-zA-Z]+', text_before):
                    text_before_clean = self._clean_latex_text(text_before)
                    if text_before_clean:
                        # Add to previous element if it was an equation
                        if enhanced_elements and enhanced_elements[-1]['type'] == 'equation':
                            if 'explanation' not in enhanced_elements[-1]:
                                enhanced_elements[-1]['explanation'] = text_before_clean
                            else:
                                enhanced_elements[-1]['explanation'] += ' ' + text_before_clean
            
            # Add current element
            enhanced_elements.append(element.copy())
            
            # Get text after this element (until next element or end)
            next_start = all_elements[i + 1]['start'] if i + 1 < len(all_elements) else len(content)
            text_after = content[element['end']:next_start].strip()
            
            if text_after and not re.match(r'^\\[a-zA-Z]+', text_after):
                text_after_clean = self._clean_latex_text(text_after)
                if text_after_clean:
                    if element['type'] == 'equation':
                        # Attach explanation to this equation
                        enhanced_elements[-1]['explanation'] = text_after_clean
                    else:
                        # Create separate explanation node for non-equations
                        enhanced_elements.append({
                            'type': 'explanation',
                            'content': text_after_clean,
                            'title': 'Explanation',
                            'start': element['end'],
                            'end': next_start
                        })
            
            last_end = next_start
        
        # Create nodes from enhanced elements
        for element in enhanced_elements:
            if element['type'] == 'equation':
                if 'explanation' in element and element['explanation']:
                    # Create equation node that is both formula and expandable explanation
                    equation_node = MindMapNode(
                        title="Key Equation",
                        content=f"$${element['content']}$$ {element['explanation']}",
                        node_type="equation_with_explanation",
                        level=section_node.level + 1
                    )
                else:
                    # Simple equation node
                    equation_node = MindMapNode(
                        title="Key Equation",
                        content=f"$${element['content']}$$",
                        node_type="equation",
                        level=section_node.level + 1
                    )
                section_node.add_child(equation_node)
                
            elif element['type'] == 'theorem':
                theorem_node = MindMapNode(
                    title=element['title'],
                    content=element['content'],
                    node_type="theorem",
                    level=section_node.level + 1
                )
                section_node.add_child(theorem_node)
                
            elif element['type'] == 'paragraph':
                para_node = MindMapNode(
                    title=element['title'],
                    content=element['content'],
                    node_type="paragraph",
                    level=section_node.level + 1
                )
                section_node.add_child(para_node)
                
            elif element['type'] == 'explanation':
                explanation_node = MindMapNode(
                    title=element['title'],
                    content=element['content'],
                    node_type="explanation",
                    level=section_node.level + 1
                )
                section_node.add_child(explanation_node)
    
    def _extract_remaining_text_content(self, content: str, processed_positions: set) -> str:
        """Extract text content that wasn't processed as equations or environments."""
        # Split content into chunks and find unprocessed text
        all_matches = []
        
        # Find all equation/environment positions
        patterns = [
            r'\\begin\{(align|equation|gather)\}(.*?)\\end\{\1\}',
            r'\\\[(.*?)\\\]',
            r'\$\$(.*?)\$\$',
            r'\\paragraph\{([^}]*)\}([^\\]*?)(?=\\|\Z)',
            r'\\begin\{(' + '|'.join(self.THEOREM_ENVS) + r')\}(.*?)\\end\{\1\}'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                all_matches.append((match.start(), match.end()))
        
        # Sort matches by position
        all_matches.sort()
        
        # Extract text between and after matches
        remaining_text_parts = []
        last_end = 0
        
        for start, end in all_matches:
            # Text before this match
            if start > last_end:
                text_chunk = content[last_end:start].strip()
                if text_chunk and not re.match(r'^\\[a-zA-Z]+', text_chunk):  # Skip LaTeX commands
                    remaining_text_parts.append(text_chunk)
            last_end = end
        
        # Text after last match
        if last_end < len(content):
            text_chunk = content[last_end:].strip()
            if text_chunk and not re.match(r'^\\[a-zA-Z]+', text_chunk):
                remaining_text_parts.append(text_chunk)
        
        # Join and clean the remaining text
        remaining_text = ' '.join(remaining_text_parts)
        return self._clean_latex_text(remaining_text) if remaining_text else ""
    
    def _add_content_to_current_section(self, content: str, section_stack: Dict[int, MindMapNode]) -> None:
        """Add content to the current deepest section."""
        current_section = section_stack.get(max(section_stack.keys()))
        if not current_section:
            return
        
        # Look for theorem environments
        theorem_pattern = r'\\begin\{(' + '|'.join(self.THEOREM_ENVS) + r')\}(.*?)\\end\{\1\}'
        for match in re.finditer(theorem_pattern, content, re.DOTALL):
            env_name = match.group(1)
            env_content = self._clean_latex_text(match.group(2))
            
            # Special handling: if this is a definition and the current section has no content yet,
            # merge it into the section title instead of creating a separate child
            if env_name == 'definition' and not current_section.content and not current_section.children:
                current_section.content = env_content
                current_section.node_type = 'section_with_definition'
            else:
                theorem_node = MindMapNode(
                    title=f"{env_name.title()}",
                    content=env_content,
                    node_type=env_name,
                    level=current_section.level + 1
                )
                current_section.add_child(theorem_node)
        
        # Look for equations
        equation_pattern = r'\\begin\{equation\}(.*?)\\end\{equation\}'
        for match in re.finditer(equation_pattern, content, re.DOTALL):
            eq_content = match.group(1).strip()
            equation_node = MindMapNode(
                title="Equation",
                content=f"$${eq_content}$$",
                node_type="equation",
                level=current_section.level + 1
            )
            current_section.add_child(equation_node)
    
    def _clean_latex_text(self, text: str) -> str:
        """Clean LaTeX markup from text while preserving math expressions."""
        import re
        
        # First, protect inline math expressions
        math_expressions = []
        
        def replace_math(match):
            math_expressions.append(match.group(0))
            return f"__MATH_PLACEHOLDER_{len(math_expressions)-1}__"
        
        # Protect both $...$ and \(...\) math
        text_protected = re.sub(r'\$([^$]+)\$', replace_math, text)
        text_protected = re.sub(r'\\?\\\(([^)]+)\\\)', replace_math, text_protected)
        
        # Remove common LaTeX commands (but not math)
        text_protected = re.sub(r'\\[a-zA-Z]+\*?\{([^}]*)\}', r'\1', text_protected)  # \command{text} -> text
        text_protected = re.sub(r'\\[a-zA-Z]+\*?(?!\()', '', text_protected)  # Remove commands without args, but not \(
        text_protected = re.sub(r'\{([^}]*)\}', r'\1', text_protected)  # Remove braces
        text_protected = re.sub(r'\\\\', ' ', text_protected)  # Line breaks
        text_protected = re.sub(r'[~]', ' ', text_protected)  # Non-breaking spaces
        text_protected = re.sub(r'\s+', ' ', text_protected)  # Multiple spaces
        
        # Restore math expressions
        for i, math_expr in enumerate(math_expressions):
            text_protected = text_protected.replace(f"__MATH_PLACEHOLDER_{i}__", math_expr)
        
        return text_protected.strip()


class MindMapFormatter:
    """Formats mind map tree for different output formats."""
    
    @staticmethod
    def _format_text_for_display(text: str) -> str:
        """Format text for better display in HTML details while preserving math."""
        import re
        
        # Don't convert any math in explanations - let Markmap handle it
        # Just clean up the text and format it nicely
        
        # Split into sentences for better readability
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted_sentences = []
        
        current_paragraph = []
        for sentence in sentences:
            current_paragraph.append(sentence.strip())
            # Start new paragraph after ~3 sentences or at logical breaks
            if (len(current_paragraph) >= 3 or 
                any(word in sentence.lower() for word in ['therefore', 'thus', 'however', 'moreover', 'furthermore'])):
                formatted_sentences.append(' '.join(current_paragraph))
                current_paragraph = []
        
        # Add remaining sentences
        if current_paragraph:
            formatted_sentences.append(' '.join(current_paragraph))
        
        # Join paragraphs with HTML breaks
        return '<br><br>'.join(formatted_sentences)
    
    @staticmethod
    def to_markdown(root: MindMapNode, max_depth: int = 10, markmap_mode: bool = False, truncate_at: int = 100) -> str:
        """Convert mind map tree to markdown nested list."""
        def format_node(node: MindMapNode, depth: int = 0) -> str:
            if depth > max_depth:
                return ""
            
            indent = "  " * depth
            bullet = "-"
            
            # Format title with content
            title = node.title
            
            if node.content and node.content != node.title:
                # Special handling for equations with explanations first
                if node.node_type == 'equation_with_explanation' and markmap_mode:
                    # Parse formula and explanation
                    if '$$' in node.content:
                        parts = node.content.split('$$')
                        if len(parts) >= 3:  # $$formula$$ explanation
                            formula = f"$${parts[1]}$$"
                            explanation = '$$'.join(parts[2:]).strip()
                            if explanation:
                                explanation_formatted = MindMapFormatter._format_text_for_display(explanation)
                                title = f"{title} {formula} <details><summary>📊 Explanation</summary><div style='max-width:400px;text-align:left;line-height:1.4;'>{explanation_formatted}</div></details>"
                            else:
                                title = f"{title} {formula}"
                        else:
                            title = f"{title} {node.content}"
                elif markmap_mode and len(node.content) > truncate_at:
                    # Use HTML details/summary for long content in Markmap mode
                    short_title = title if len(title) <= 50 else title[:47] + "..."
                    if node.content.startswith('$'):
                        # Math content - keep it visible
                        title = f"{short_title} {node.content}"
                    elif node.node_type == 'equation_with_explanation':
                        # Special handling for equations with explanations - show formula + expandable explanation
                        content_parts = node.content.split('$$ ', 1)
                        if len(content_parts) == 2:
                            formula = content_parts[0] + '$$'
                            explanation = content_parts[1].strip()
                            title = f"{short_title} {formula} <details><summary>📊 Explanation</summary><div style='max-width:400px;text-align:left;line-height:1.4;'>{MindMapFormatter._format_text_for_display(explanation)}</div></details>"
                        else:
                            # Fallback if parsing fails
                            title = f"{short_title} <details><summary>📊 Details</summary><div style='max-width:400px;text-align:left;line-height:1.4;'>{MindMapFormatter._format_text_for_display(node.content.replace('\\n', ' ').strip())}</div></details>"
                    else:
                        # Long text content - make it expandable with proper formatting
                        content_clean = node.content.replace('\n', ' ').strip()
                        # Break long text into sentences for better readability
                        content_formatted = MindMapFormatter._format_text_for_display(content_clean)
                        # Special label for definitions merged into sections
                        summary_label = "📖 Definition" if node.node_type == 'section_with_definition' else "📖 Details"
                        title = f"{short_title} <details><summary>{summary_label}</summary><div style='max-width:400px;text-align:left;line-height:1.4;'>{content_formatted}</div></details>"
                elif len(node.content) > 200:
                    content_preview = node.content[:200] + "..."
                    if not node.content.startswith('$'):
                        title += f": {content_preview}"
                    else:
                        title += f" {node.content}"
                else:
                    if not node.content.startswith('$'):
                        title += f": {node.content}"
                    else:
                        title += f" {node.content}"
            
            result = f"{indent}{bullet} {title}\n"
            
            # Add children
            for child in node.children:
                result += format_node(child, depth + 1)
            
            return result
        
        markdown = f"# {root.title}\n\n"
        for child in root.children:
            markdown += format_node(child, 0)
        
        return markdown
    
    @staticmethod
    def to_json(root: MindMapNode) -> str:
        """Convert mind map tree to JSON format."""
        return json.dumps(root.to_dict(), indent=2, ensure_ascii=False)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert LaTeX documents to mind map structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python latex_to_mindmap.py paper.tex --format markdown --output mindmap.md
  python latex_to_mindmap.py thesis.tex --format json --output mindmap.json
  python latex_to_mindmap.py notes.tex  # Default: markdown to stdout
        """
    )
    
    parser.add_argument('input', help='Input LaTeX file (.tex)')
    parser.add_argument('--format', choices=['markdown', 'json'], 
                       default='markdown', help='Output format (default: markdown)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximum nesting depth for markdown (default: 10)')
    parser.add_argument('--markmap-mode', action='store_true',
                       help='Optimize for Markmap with expandable text nodes')
    parser.add_argument('--truncate-at', type=int, default=100,
                       help='Truncate node titles at N characters for Markmap (default: 100)')
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File {input_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            tex_content = f.read()
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        with open(input_path, 'r', encoding='latin-1') as f:
            tex_content = f.read()
    
    # Parse LaTeX content
    parser_instance = LatexParser(tex_content)
    mind_map_root = parser_instance.parse()
    
    # Format output
    formatter = MindMapFormatter()
    
    if args.format == 'markdown':
        output_content = formatter.to_markdown(mind_map_root, args.max_depth, args.markmap_mode, args.truncate_at)
    else:  # json
        output_content = formatter.to_json(mind_map_root)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Mind map saved to {output_path}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()