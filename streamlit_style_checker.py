#!/usr/bin/env python3
"""
Nutanix Documentation Style Checker - Streamlit Web App

A web-based interface for checking XML documentation against Nutanix style guidelines.
Users can paste XML content and receive real-time style recommendations.
"""

import streamlit as st
import yaml
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import io
from html.parser import HTMLParser
from xml.parsers.expat import ExpatError
import html

@dataclass
class StyleIssue:
    """Represents a style guide violation"""
    line_number: int
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    rule: str
    suggestion: str = ""
    original_text: str = ""  # The original text that triggered the issue
    auto_fix: Optional[str] = None  # Automatically generated fix
    can_auto_fix: bool = False  # Whether this issue can be automatically fixed

@dataclass
class AutoFix:
    """Represents an automatic fix for a style issue"""
    issue_id: str
    original_text: str
    fixed_text: str
    line_number: int
    description: str
    confidence: str  # 'high', 'medium', 'low'

class StyleFixer:
    """Handles automatic fixing of style issues"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.fixes_applied = []
        
    def generate_fixes(self, content: str, issues: List[StyleIssue]) -> List[AutoFix]:
        """Generate automatic fixes for applicable issues"""
        auto_fixes = []
        lines = content.split('\n')
        
        for i, issue in enumerate(issues):
            if issue.can_auto_fix:
                fix = self._create_fix_for_issue(issue, lines, i)
                if fix:
                    auto_fixes.append(fix)
                    
        return auto_fixes
    
    def apply_fixes(self, content: str, fixes: List[AutoFix]) -> str:
        """Apply a list of fixes to content"""
        lines = content.split('\n')
        
        # Sort fixes by line number in reverse order to avoid index shifting
        sorted_fixes = sorted(fixes, key=lambda f: f.line_number, reverse=True)
        
        for fix in sorted_fixes:
            if fix.line_number <= len(lines):
                line_idx = fix.line_number - 1
                lines[line_idx] = lines[line_idx].replace(fix.original_text, fix.fixed_text)
                self.fixes_applied.append(fix)
                
        return '\n'.join(lines)
    
    def _create_fix_for_issue(self, issue: StyleIssue, lines: List[str], issue_id: int) -> Optional[AutoFix]:
        """Create a specific fix for an issue based on its rule"""
        if issue.line_number > len(lines):
            return None
            
        line = lines[issue.line_number - 1]
        
        # Rule-specific fixes
        if issue.rule == 'capitalization' and 'heading' in issue.message.lower():
            return self._fix_heading_capitalization(issue, line, issue_id)
        elif issue.rule == 'contractions':
            return self._fix_contractions(issue, line, issue_id)
        elif issue.rule == 'oxford_comma':
            return self._fix_oxford_comma(issue, line, issue_id)
        elif issue.rule == 'deprecated_terms':
            return self._fix_deprecated_terms(issue, line, issue_id)
        elif issue.rule == 'voice_and_mood':
            return self._fix_passive_voice(issue, line, issue_id)
        elif issue.rule == 'approved_phrasing':
            return self._fix_approved_phrasing(issue, line, issue_id)
        elif issue.rule == 'hyphens':
            return self._fix_compound_adjectives(issue, line, issue_id)
        elif issue.rule == 'quotes':
            return self._fix_quotes(issue, line, issue_id)
            
        return None
    
    def _fix_heading_capitalization(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Fix heading capitalization to sentence case"""
        # Extract heading text from HTML/XML
        heading_match = re.search(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', line)
        if heading_match:
            original_heading = heading_match.group(1)
            fixed_heading = self._convert_to_sentence_case(original_heading)
            if original_heading != fixed_heading:
                fixed_line = line.replace(original_heading, fixed_heading)
                return AutoFix(
                    issue_id=str(issue_id),
                    original_text=original_heading,
                    fixed_text=fixed_heading,
                    line_number=issue.line_number,
                    description=f"Convert heading to sentence case",
                    confidence="high"
                )
        return None
    
    def _fix_contractions(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Fix problematic contractions"""
        contractions_map = {
            "should've": "should have",
            "could've": "could have", 
            "would've": "would have",
            "shouldn't": "should not",
            "couldn't": "could not",
            "wouldn't": "would not"
        }
        
        for contraction, expansion in contractions_map.items():
            if contraction.lower() in line.lower():
                # Find the exact case in the line
                pattern = re.compile(re.escape(contraction), re.IGNORECASE)
                match = pattern.search(line)
                if match:
                    original = match.group()
                    # Preserve capitalization of first letter
                    if original[0].isupper():
                        fixed = expansion.capitalize()
                    else:
                        fixed = expansion
                    
                    return AutoFix(
                        issue_id=str(issue_id),
                        original_text=original,
                        fixed_text=fixed,
                        line_number=issue.line_number,
                        description=f"Expand contraction '{original}' to '{fixed}'",
                        confidence="high"
                    )
        return None
    
    def _fix_oxford_comma(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Add missing Oxford comma"""
        # Look for pattern like "A, B and C" and change to "A, B, and C"
        pattern = r'(\w+),\s+(\w+)\s+and\s+(\w+)'
        match = re.search(pattern, line)
        if match:
            original = match.group(0)
            fixed = f"{match.group(1)}, {match.group(2)}, and {match.group(3)}"
            return AutoFix(
                issue_id=str(issue_id),
                original_text=original,
                fixed_text=fixed,
                line_number=issue.line_number,
                description="Add Oxford comma",
                confidence="high"
            )
        return None
    
    def _fix_deprecated_terms(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Replace deprecated terms with current ones"""
        terminology = self.config.get('style_guide', {}).get('terminology', {})
        deprecated_terms = terminology.get('deprecated_terms', {})
        
        for old_term, replacement_info in deprecated_terms.items():
            current_term = replacement_info.get('current_term', '')
            if old_term.lower() in line.lower() and current_term != "Remove; no longer useful":
                # Find exact case in line
                pattern = re.compile(re.escape(old_term), re.IGNORECASE)
                match = pattern.search(line)
                if match:
                    original = match.group()
                    # Preserve capitalization
                    if original[0].isupper():
                        fixed = current_term.capitalize()
                    else:
                        fixed = current_term
                    
                    return AutoFix(
                        issue_id=str(issue_id),
                        original_text=original,
                        fixed_text=fixed,
                        line_number=issue.line_number,
                        description=f"Replace deprecated term '{original}' with '{fixed}'",
                        confidence="high"
                    )
        return None
    
    def _fix_approved_phrasing(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Fix unapproved phrasing with approved alternatives"""
        phrasing_fixes = {
            "the node is down": "the node is unresponsive or unavailable",
            "the node is dead": "the node is unresponsive or unavailable",
            "the data is corrupted": "there is a potential data integrity issue",
            "kill the service": "stop the service",
            "kill the process": "stop the process",
            "the service crashed": "the service stopped unexpectedly",
            "the drive is bad": "the drive has a fault",
            "the drive is broken": "the drive has a fault"
        }
        
        for bad_phrase, good_phrase in phrasing_fixes.items():
            if bad_phrase.lower() in line.lower():
                pattern = re.compile(re.escape(bad_phrase), re.IGNORECASE)
                match = pattern.search(line)
                if match:
                    original = match.group()
                    # Preserve sentence capitalization
                    if original[0].isupper():
                        fixed = good_phrase.capitalize()
                    else:
                        fixed = good_phrase
                    
                    return AutoFix(
                        issue_id=str(issue_id),
                        original_text=original,
                        fixed_text=fixed,
                        line_number=issue.line_number,
                        description=f"Use approved phrasing",
                        confidence="high"
                    )
        return None
    
    def _fix_compound_adjectives(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Add hyphens to compound adjectives"""
        compounds = {
            "single node": "single-node",
            "command line": "command-line", 
            "health check": "health-check",
            "real time": "real-time",
            "multi node": "multi-node"
        }
        
        for unhyphenated, hyphenated in compounds.items():
            # Look for the compound followed by a noun
            pattern = f"\\b{re.escape(unhyphenated)}\\s+(\\w+)"
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                original = match.group(0)
                fixed = original.replace(unhyphenated, hyphenated)
                return AutoFix(
                    issue_id=str(issue_id),
                    original_text=unhyphenated,
                    fixed_text=hyphenated,
                    line_number=issue.line_number,
                    description=f"Add hyphen to compound adjective",
                    confidence="medium"
                )
        return None
    
    def _fix_quotes(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Convert single quotes to double quotes for UI text"""
        # Look for single quotes around what appears to be UI text
        pattern = r"'([^']*(?:click|button|menu|dialog|error|alert|warning)[^']*)'"
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            original_with_quotes = match.group(0)
            content = match.group(1)
            fixed_with_quotes = f'"{content}"'
            return AutoFix(
                issue_id=str(issue_id),
                original_text=original_with_quotes,
                fixed_text=fixed_with_quotes,
                line_number=issue.line_number,
                description="Use double quotes for UI text",
                confidence="medium"
            )
        return None
    
    def _fix_passive_voice(self, issue: StyleIssue, line: str, issue_id: int) -> Optional[AutoFix]:
        """Suggest active voice alternatives (high-confidence cases only)"""
        # Only handle very clear cases
        passive_patterns = {
            "is set by": "sets",
            "are set by": "set",
            "is restarted by": "restarts",
            "are restarted by": "restart"
        }
        
        for passive, active in passive_patterns.items():
            if passive in line.lower():
                # This is a complex transformation, mark as low confidence
                return AutoFix(
                    issue_id=str(issue_id),
                    original_text=passive,
                    fixed_text=active,
                    line_number=issue.line_number,
                    description="Convert to active voice (review suggested change)",
                    confidence="low"
                )
        return None
    
    def _convert_to_sentence_case(self, text: str) -> str:
        """Convert text to sentence case, preserving acronyms"""
        words = text.split()
        if not words:
            return text
            
        # Known acronyms that should stay capitalized
        acronyms = {'AOS', 'AHV', 'CVM', 'NCC', 'DSF', 'PC', 'PE', 'NC2', 'API', 'UI', 'CLI', 'SSH', 'IP', 'VM', 'CPU', 'RAM', 'SSD', 'HDD', 'KB'}
        
        result = []
        for i, word in enumerate(words):
            if i == 0:
                # First word is always capitalized
                result.append(word.capitalize())
            elif word.upper() in acronyms:
                # Keep acronyms uppercase
                result.append(word.upper())
            elif word.lower() in ['a', 'an', 'the', 'and', 'or', 'but', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in', 'with']:
                # Articles and prepositions lowercase
                result.append(word.lower())
            else:
                # Everything else lowercase
                result.append(word.lower())
                
        return ' '.join(result)

class ContentExtractor:
    """Extract text content from HTML/XML while preserving structure info"""
    
    def __init__(self):
        self.text_content = []
        self.line_mapping = {}  # Maps extracted content line to original line
        self.headings = []  # Track headings with their levels
        
    def extract_content(self, markup: str) -> Tuple[List[str], Dict[int, int], List[Tuple[int, str, str]]]:
        """Extract text content from HTML/XML markup
        
        Returns:
            - List of text lines
            - Mapping from content line number to original line number  
            - List of headings (level, text, original_line)
        """
        self.text_content = []
        self.line_mapping = {}
        self.headings = []
        
        original_lines = markup.split('\n')
        
        # Try to parse as XML first, then fall back to HTML parsing
        try:
            self._extract_from_xml(markup, original_lines)
        except (ExpatError, ET.ParseError):
            self._extract_from_html(markup, original_lines)
            
        return self.text_content, self.line_mapping, self.headings
    
    def _extract_from_xml(self, markup: str, original_lines: List[str]):
        """Extract content from XML using ElementTree"""
        # Add a root element if not present to make it valid XML
        if not markup.strip().startswith('<?xml') and not re.match(r'^\s*<[^>]+>', markup.strip()):
            markup = f"<root>{markup}</root>"
        elif not markup.strip().startswith('<'):
            # Plain text content
            self._extract_plain_text(markup, original_lines)
            return
            
        try:
            root = ET.fromstring(markup)
            self._walk_xml_tree(root, original_lines)
        except ET.ParseError:
            # Fall back to HTML parsing
            self._extract_from_html(markup, original_lines)
    
    def _extract_from_html(self, markup: str, original_lines: List[str]):
        """Extract content from HTML using custom parser"""
        parser = HTMLContentParser(original_lines)
        parser.feed(markup)
        self.text_content = parser.text_content
        self.line_mapping = parser.line_mapping
        self.headings = parser.headings
    
    def _extract_plain_text(self, text: str, original_lines: List[str]):
        """Handle plain text content"""
        for i, line in enumerate(original_lines):
            if line.strip():
                self.text_content.append(line.strip())
                self.line_mapping[len(self.text_content)] = i + 1
    
    def _walk_xml_tree(self, element: ET.Element, original_lines: List[str]):
        """Walk XML tree and extract text content"""
        # Handle text content
        if element.text and element.text.strip():
            text = element.text.strip()
            self.text_content.append(text)
            # Try to find the original line (simplified)
            line_num = self._find_text_line(text, original_lines)
            self.line_mapping[len(self.text_content)] = line_num
            
            # Check if this is a heading
            if element.tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.tag.lower()[1])
                self.headings.append((level, text, line_num))
        
        # Recursively process children
        for child in element:
            self._walk_xml_tree(child, original_lines)
            
            # Handle tail text
            if child.tail and child.tail.strip():
                text = child.tail.strip()
                self.text_content.append(text)
                line_num = self._find_text_line(text, original_lines)
                self.line_mapping[len(self.text_content)] = line_num
    
    def _find_text_line(self, text: str, original_lines: List[str]) -> int:
        """Find the original line number containing the text"""
        for i, line in enumerate(original_lines):
            if text in line:
                return i + 1
        return 1  # Default to line 1 if not found

class HTMLContentParser(HTMLParser):
    """Custom HTML parser to extract text content with line tracking"""
    
    def __init__(self, original_lines: List[str]):
        super().__init__()
        self.original_lines = original_lines
        self.text_content = []
        self.line_mapping = {}
        self.headings = []
        self.current_heading_level = None
        
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        if tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_heading_level = int(tag.lower()[1])
    
    def handle_endtag(self, tag: str):
        if tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_heading_level = None
    
    def handle_data(self, data: str):
        text = data.strip()
        if text:
            self.text_content.append(text)
            line_num = self._find_text_line(text)
            self.line_mapping[len(self.text_content)] = line_num
            
            if self.current_heading_level:
                self.headings.append((self.current_heading_level, text, line_num))
    
    def _find_text_line(self, text: str) -> int:
        """Find the original line number containing the text"""
        for i, line in enumerate(self.original_lines):
            if text in line:
                return i + 1
        return 1

class StreamlitStyleChecker:
    """Streamlit-specific style checker class"""
    
    def __init__(self, config_path: str = ".styleguide.yaml"):
        self.config = self._load_config(config_path)
        self.issues: List[StyleIssue] = []
        self.fixer = StyleFixer(self.config)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load style guide configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            st.error(f"Error: Style guide config file '{config_path}' not found")
            return {}
        except yaml.YAMLError as e:
            st.error(f"Error parsing config file: {e}")
            return {}
    
    def check_content(self, content: str) -> List[StyleIssue]:
        """Check content against the style guide"""
        self.issues = []
        
        if not content.strip():
            return self.issues
        
        # Extract text content from HTML/XML
        extractor = ContentExtractor()
        text_lines, line_mapping, headings = extractor.extract_content(content)
        
        # Store for use in other methods
        self.line_mapping = line_mapping
        self.headings = headings
        self.original_lines = content.split('\n')
        
        # Check extracted content
        self._check_extracted_content(text_lines)
        
        # Check document structure
        self._check_document_content_structure(text_lines)
        
        # Check multi-line patterns
        self._check_multi_line_patterns(text_lines)
        
        return self.issues
    
    def _check_document_content_structure(self, text_lines: List[str]):
        """Check document structure based on content patterns"""
        content_text = '\n'.join(text_lines).lower()
        
        # Check for table of contents mention
        if 'table of contents' not in content_text and len(text_lines) > 20:
            self.issues.append(StyleIssue(
                line_number=1,
                severity='info',
                category='Document Structure',
                message="Long document without Table of Contents",
                rule='table_of_contents',
                suggestion="Consider adding a Table of Contents for documents with multiple sections",
                original_text=""
            ))
        
        # Check heading structure
        if len(self.headings) > 1:
            # Check for proper heading hierarchy
            prev_level = 0
            for level, text, line_num in self.headings:
                if level > prev_level + 1:
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Document Structure',
                        message=f"Heading level {level} skips levels (previous was {prev_level})",
                        rule='heading_hierarchy',
                        suggestion="Use sequential heading levels (h1, h2, h3) without skipping",
                        original_text=text
                    ))
                prev_level = level
    
    def _check_extracted_content(self, text_lines: List[str]):
        """Check extracted text content line by line against all style guidelines"""
        
        for content_line_num, line in enumerate(text_lines, 1):
            if not line.strip():
                continue
                
            # Get original line number for reporting
            original_line_num = self.line_mapping.get(content_line_num, content_line_num)
                
            # Check all major style guideline categories
            self._check_grammar_and_mechanics(line, original_line_num)
            self._check_writing_standards(line, original_line_num)
            self._check_content_quality(line, original_line_num)
            self._check_formatting_standards(line, original_line_num)
            self._check_training_standards(line, original_line_num)
            self._check_technical_content(line, original_line_num)
        
        # Check headings specifically
        self._check_headings()
        
        # Check for specific multi-line content patterns
        self._check_document_patterns(text_lines)
        
        # Check content accessibility
        self._check_content_accessibility(text_lines)
    
    def _check_writing_standards(self, line: str, line_num: int):
        """Check writing standards based on new style guide format"""
        style_guide = self.config.get('style_guide', {})
        grammar_mechanics = style_guide.get('grammar_and_mechanics', {})
        
        # Check voice and mood
        voice_mood = grammar_mechanics.get('voice_and_mood', {})
        if voice_mood.get('preferred') == 'active_voice_imperative':
            # Check for passive voice indicators
            passive_indicators = ['is set', 'are set', 'was set', 'were set', 'is monitored', 'are monitored', 
                                'is performed', 'are performed', 'is created', 'are created']
            for indicator in passive_indicators:
                if indicator in line.lower():
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Grammar and Mechanics',
                        message=f"Passive voice detected: '{indicator}'",
                        rule='voice_and_mood',
                        suggestion="Use active voice and imperative mood. Example: 'Run the NCC health check' instead of 'The NCC health check should be run'"
                    ))
        
        # Check contractions policy
        contractions_config = grammar_mechanics.get('contractions', {})
        if contractions_config.get('policy') == 'use_sparingly':
            # Check for contractions that should be avoided
            avoid_contractions = ["should've", "could've", "would've", "shouldn't", "couldn't", "wouldn't"]
            for contraction in avoid_contractions:
                if contraction in line.lower():
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Grammar and Mechanics',
                        message=f"Contraction '{contraction}' should be avoided",
                        rule='contractions',
                        suggestion=f"Use full form: {contraction} → {self._expand_contraction(contraction)}",
                        original_text=contraction,
                        can_auto_fix=True
                    ))
        
        # Check for third-person references (should use "you")
        third_person_refs = ["the end user", "the user", "the customer", "users can", "customers can"]
        for ref in third_person_refs:
            if ref in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Grammar and Mechanics',
                    message=f"Third-person reference: '{ref}'",
                    rule='direct_address',
                    suggestion="Use 'you' to address the reader directly"
                ))
        
        # Check for approved phrasing violations
        terminology = style_guide.get('terminology', {})
        approved_phrasing = terminology.get('approved_phrasing', {})
        avoid_terms = approved_phrasing.get('avoid_terms', [])
        
        for term in avoid_terms:
            if term.lower() in line.lower():
                preferred_terms = approved_phrasing.get('preferred_terms', {})
                suggestion = "Use calm, precise language"
                if term.lower() == "the node is down/dead":
                    suggestion = "Use: 'The node is unresponsive or unavailable.'"
                elif term.lower() == "the data is corrupted":
                    suggestion = "Use: 'There is a potential data integrity issue.'"
                
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Terminology',
                    message=f"Avoid term: '{term}'",
                    rule='approved_phrasing',
                    suggestion=suggestion,
                    original_text=term,
                    can_auto_fix=True
                ))
    
    def _check_headings(self):
        """Check heading-specific rules"""
        style_guide = self.config.get('style_guide', {})
        grammar_mechanics = style_guide.get('grammar_and_mechanics', {})
        capitalization = grammar_mechanics.get('capitalization', {})
        
        if capitalization.get('rule') == 'sentence_case':
            for level, heading_text, line_num in self.headings:
                words = heading_text.split()
                if len(words) > 1:
                    # Check if more than first word is capitalized (excluding proper nouns/acronyms)
                    known_acronyms = ['AOS', 'AHV', 'CVM', 'NCC', 'DSF', 'PC', 'PE', 'NC2', 'API', 'UI', 'CLI', 'SSH', 'IP', 'VM', 'CPU', 'RAM', 'SSD', 'HDD']
                    capitalized_count = sum(1 for word in words[1:] if word[0].isupper() and word.upper() not in known_acronyms and not word.istitle())
                    if capitalized_count > 0:
                        self.issues.append(StyleIssue(
                            line_number=line_num,
                            severity='warning',
                            category='Grammar and Mechanics',
                            message=f"Heading should use sentence case: '{heading_text}'",
                            rule='capitalization',
                            suggestion="Use sentence case - capitalize only the first word and proper nouns/acronyms",
                            original_text=heading_text,
                            can_auto_fix=True
                        ))
    
    def _check_grammar_and_mechanics(self, line: str, line_num: int):
        """Check grammar and mechanics rules from the new style guide"""
        style_guide = self.config.get('style_guide', {})
        grammar_mechanics = style_guide.get('grammar_and_mechanics', {})
        
        # Check punctuation - Oxford comma
        punctuation = grammar_mechanics.get('punctuation', {})
        oxford_comma = punctuation.get('oxford_comma', {})
        if oxford_comma.get('rule') == 'always_use':
            # Look for lists with 3+ items missing Oxford comma
            comma_lists = re.findall(r'\b\w+,\s+\w+\s+and\s+\w+', line)
            for match in comma_lists:
                if ', and' not in match:
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='info',
                        category='Grammar and Mechanics',
                        message=f"Missing Oxford comma in: '{match}'",
                        rule='oxford_comma',
                        suggestion="Always use Oxford comma in lists of three or more items",
                        original_text=match,
                        can_auto_fix=True
                    ))
        
        # Check hyphens in compound adjectives
        hyphens = punctuation.get('hyphens', {})
        if hyphens.get('rule') == 'compound_adjectives':
            # Check for common compound adjectives that should be hyphenated
            compound_patterns = [
                (r'\bsingle node\b', 'single-node'),
                (r'\bcommand line\b', 'command-line'),
                (r'\bhealth check\b', 'health-check'),
                (r'\breal time\b', 'real-time'),
                (r'\bmulti node\b', 'multi-node')
            ]
            
            for pattern, suggestion in compound_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's before a noun (simplified check)
                    match = re.search(pattern + r'\s+\w+', line, re.IGNORECASE)
                    if match:
                        self.issues.append(StyleIssue(
                            line_number=line_num,
                            severity='info',
                            category='Grammar and Mechanics',
                            message=f"Compound adjective should be hyphenated: '{match.group()}'",
                            rule='hyphens',
                            suggestion=f"Use '{suggestion}' when it modifies a noun",
                            original_text=match.group()
                        ))
        
        # Check quotes usage
        quotes = punctuation.get('quotes', {})
        if quotes.get('rule') == 'double_quotes':
            # Look for single quotes around UI text that should be double quotes
            single_quote_matches = re.findall(r"'([^']+)'", line)
            for match in single_quote_matches:
                # Heuristic: if it looks like UI text or file names
                if any(indicator in match.lower() for indicator in ['click', 'button', 'menu', 'dialog', '.xml', '.log', 'error', 'alert']):
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='info',
                        category='Grammar and Mechanics',
                        message=f"Use double quotes for UI text: '{match}'",
                        rule='quotes',
                        suggestion="Use double quotes for UI text, alerts, file names, or input strings",
                        original_text=f"'{match}'"
                    ))
        
        # Check list structure
        lists = grammar_mechanics.get('lists', {})
        if lists.get('parallel_structure', {}).get('required'):
            # This is a complex check that would need more context
            # For now, just check for obvious parallel structure violations
            if re.match(r'^\s*[-*]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                # Check if list item starts with different grammatical structures
                list_item = re.sub(r'^\s*[-*\d.]+\s+', '', line).strip()
                if list_item:
                    # Check for mixing imperative and gerund forms (simplified)
                    if list_item.lower().startswith(('check', 'verify', 'run', 'click', 'enter')):
                        # Imperative form - good
                        pass
                    elif list_item.lower().startswith(('checking', 'verifying', 'running')):
                        # Gerund form - suggest consistency
                        self.issues.append(StyleIssue(
                            line_number=line_num,
                            severity='info',
                            category='Grammar and Mechanics',
                            message="List items should have parallel structure",
                            rule='parallel_structure',
                            suggestion="Use consistent grammatical structure across all list items (all imperatives or all gerunds)",
                            original_text=list_item
                        ))
    
    def _expand_contraction(self, contraction: str) -> str:
        """Expand contractions to full forms"""
        expansions = {
            "won't": "will not", "don't": "do not", "can't": "cannot",
            "shouldn't": "should not", "couldn't": "could not", "wouldn't": "would not",
            "isn't": "is not", "aren't": "are not", "should've": "should have",
            "could've": "could have", "would've": "would have"
        }
        return expansions.get(contraction.lower(), contraction)
    
    def _check_content_quality(self, line: str, line_num: int):
        """Check content quality standards from KB guidelines"""
        content_quality = self.config.get('content_quality', {})
        
        # Check for prohibited content
        prohibited = content_quality.get('technical_accuracy', {}).get('strictly_prohibited', [])
        
        # Check for negative terms
        negative_terms = ["bug", "crash", "panic", "stuck"]
        for term in negative_terms:
            if f" {term}" in line.lower() or f"{term} " in line.lower():
                alternatives = {"bug": "issue", "crash": "failure", "panic": "halt", "stuck": "no progress"}
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Content Quality',
                    message=f"Negative term '{term}' found",
                    rule='avoid_negative_terms',
                    suggestion=f"Use '{alternatives.get(term, 'alternative term')}' instead of '{term}'"
                ))
        
        # Check for non-inclusive terms
        non_inclusive = ["master/slave", "blacklist", "whitelist"]
        for term in non_inclusive:
            if term in line.lower():
                alternatives = {"master/slave": "primary/secondary", "blacklist": "deny list", "whitelist": "allow list"}
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='error',
                    category='Content Quality',
                    message=f"Non-inclusive term '{term}' found",
                    rule='inclusive_language',
                    suggestion=f"Use '{alternatives.get(term, 'inclusive alternative')}' instead"
                ))
    
    def _check_formatting_standards(self, line: str, line_num: int):
        """Check formatting standards"""
        formatting = self.config.get('formatting', {})
        
        # Check for discouraged inline styles
        text_config = formatting.get('text', {})
        discouraged_styles = text_config.get('discouraged_inline_styles', [])
        
        for style in discouraged_styles:
            if style in line:
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Formatting',
                    message=f"Discouraged inline style found: {style}",
                    rule='inline_styles',
                    suggestion="Remove inline styles and use default formatting"
                ))
    
    def _check_training_standards(self, line: str, line_num: int):
        """Check training-specific standards"""
        training = self.config.get('training_standards', {})
        
        # Check for PII violations
        pii_guidelines = training.get('pii_guidelines', {})
        prohibited = pii_guidelines.get('prohibited_content', {})
        
        # Check for IP addresses (simple pattern)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        if re.search(ip_pattern, line) and 'x.x.x.' not in line:
            self.issues.append(StyleIssue(
                line_number=line_num,
                severity='error',
                category='Training Standards',
                message="Possible real IP address found",
                rule='pii_guidelines',
                suggestion="Replace with masked format like 'x.x.x.123' or 'nutanix@cvm:x.x.x.123:~$'"
            ))
        
        # Check for email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, line) and '@nutanix.com' not in line.lower():
            self.issues.append(StyleIssue(
                line_number=line_num,
                severity='error',
                category='Training Standards',
                message="Possible email address found",
                rule='pii_guidelines',
                suggestion="Remove personal email addresses or use generic examples"
            ))
    
    
    def _check_phoenix_terminology(self, lines: List[str]):
        """Check Phoenix-specific terminology"""
        phoenix_terms = self.config.get('phoenix_specific', {}).get('terminology', {})
        consistent_terms = phoenix_terms.get('consistent_terms', [])
        
        for line_num, line in enumerate(lines, 1):
            # Check for lowercase 'phoenix' when it should be capitalized
            if re.search(r'\bphoenix\b', line) and 'Phoenix' not in line:
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Phoenix Terminology',
                    message="Found lowercase 'phoenix' - should be capitalized",
                    rule='phoenix_terminology',
                    suggestion="Use 'Phoenix' (capitalized) when referring to the tool"
                ))
    
    def _check_technical_content(self, line: str, line_num: int):
        """Check technical content standards based on new style guide format"""
        style_guide = self.config.get('style_guide', {})
        terminology = style_guide.get('terminology', {})
        
        # Check for product name consistency
        product_names = terminology.get('product_names', {})
        for product_key, product_info in product_names.items():
            full_name = product_info.get('full_name', '')
            acronym = product_info.get('acronym')
            
            # Check for proper usage of full names vs acronyms
            if full_name.lower() in line.lower():
                # Check if it's the first use and needs definition
                if acronym and f"({acronym})" not in line and acronym not in line:
                    # This is a simplistic check - in real implementation you'd track first usage
                    pass
        
        # Check abbreviation formatting
        abbreviation_rules = terminology.get('abbreviation_rules', {})
        if abbreviation_rules.get('first_use'):
            # Check for common acronyms that should be defined
            common_acronyms = ['CVM', 'AHV', 'NCC', 'AOS', 'DSF']
            for acronym in common_acronyms:
                if acronym in line and f"({acronym})" not in line:
                    # Check if full form is present
                    full_forms = {
                        'CVM': 'Controller VM',
                        'AHV': 'Nutanix AHV', 
                        'NCC': 'Nutanix Cluster Check',
                        'AOS': 'Nutanix AOS',
                        'DSF': 'Distributed Storage Fabric'
                    }
                    if full_forms.get(acronym, '').lower() not in line.lower():
                        self.issues.append(StyleIssue(
                            line_number=line_num,
                            severity='info',
                            category='Terminology',
                            message=f"Acronym '{acronym}' used without definition",
                            rule='abbreviation_rules',
                            suggestion=f"Define acronyms on first use: '{full_forms.get(acronym, acronym)} ({acronym})'"
                        ))
        
        # Check formatting for commands and processes
        formatting = terminology.get('formatting', {})
        commands = formatting.get('commands', {}).get('examples', [])
        processes = formatting.get('processes', {}).get('examples', [])
        
        # Check if commands/processes should be in monospace
        all_tech_terms = commands + processes
        for term in all_tech_terms:
            if term in line and f"`{term}`" not in line and f"<code>{term}</code>" not in line:
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Formatting',
                    message=f"Technical term '{term}' should be in monospace",
                    rule='command_formatting',
                    suggestion=f"Format as monospace: `{term}`"
                ))
        
        # Check for deprecated terms
        deprecated_terms = terminology.get('deprecated_terms', {})
        for old_term, replacement_info in deprecated_terms.items():
            current_term = replacement_info.get('current_term', '')
            if old_term.lower() in line.lower():
                if current_term != "Remove; no longer useful":
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Terminology',
                        message=f"Deprecated term '{old_term}' found",
                        rule='deprecated_terms',
                        suggestion=f"Use '{current_term}' instead of '{old_term}'",
                        original_text=old_term,
                        can_auto_fix=True
                    ))
                else:
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Terminology',
                        message=f"Deprecated term '{old_term}' should be removed",
                        rule='deprecated_terms',
                        suggestion=f"Remove '{old_term}' - no longer useful"
                    ))
    
    def _check_multi_line_patterns(self, lines: List[str]):
        """Check patterns that span multiple lines"""
        content_text = '\n'.join(lines)
        
        # Check for excessive use of warning callouts
        warning_count = content_text.lower().count('warning:')
        if warning_count > 5:
            self.issues.append(StyleIssue(
                line_number=1,
                severity='info',
                category='Content Organization',
                message=f"High number of warnings ({warning_count}) - consider if all are necessary",
                rule='callout_balance',
                suggestion="Use warnings sparingly for critical safety information only"
            ))
        
        # Check for proper code block formatting in training content
        code_blocks = re.findall(r'```([^`]+)```', content_text, re.MULTILINE | re.DOTALL)
        for i, block in enumerate(code_blocks):
            if len(block.split('\n')) > 10 and 'django' not in block.lower():
                self.issues.append(StyleIssue(
                    line_number=1,
                    severity='info',
                    category='Training Standards',
                    message="Long code block should use Django theme",
                    rule='code_block_theme',
                    suggestion="Apply Django theme for syntax highlighting on code blocks longer than 10 lines"
                ))
        
        # Check for Table of Contents patterns
        if len(lines) > 50 and not re.search(r'table\s+of\s+contents|toc', content_text, re.IGNORECASE):
            self.issues.append(StyleIssue(
                line_number=1,
                severity='info',
                category='Document Structure',
                message="Long document may benefit from Table of Contents",
                rule='toc_recommended',
                suggestion="Consider adding a Table of Contents for documents with multiple sections"
            ))
    
    def _check_document_patterns(self, lines: List[str]):
        """Check document-wide content patterns"""
        content_text = '\n'.join(lines).lower()
        
        # Check for required training sections
        training_standards = self.config.get('training_standards', {})
        module_structure = training_standards.get('module_structure', {})
        
        required_sections = module_structure.get('required_sections', [])
        for section in required_sections:
            if section.lower() not in content_text:
                self.issues.append(StyleIssue(
                    line_number=1,
                    severity='info',
                    category='Training Standards',
                    message=f"Training module missing recommended section: '{section}'",
                    rule='training_structure',
                    suggestion=f"Consider adding a '{section}' section for complete training coverage"
                ))
        
        # Check for excessive jargon or complexity indicators
        complexity_indicators = ['utilize', 'facilitate', 'implement', 'comprehensive', 'substantial']
        jargon_count = sum(content_text.count(word) for word in complexity_indicators)
        
        if jargon_count > 10:
            self.issues.append(StyleIssue(
                line_number=1,
                severity='info',
                category='Writing Standards',
                message=f"High use of complex terms ({jargon_count} instances) - consider simpler alternatives",
                rule='language_clarity',
                suggestion="Use simpler, more direct language: 'use' instead of 'utilize', 'help' instead of 'facilitate'"
            ))
        
        # Check for consistent Phoenix terminology throughout document
        phoenix_mentions = len(re.findall(r'\bphoenix\b', content_text))
        Phoenix_mentions = len(re.findall(r'\bPhoenix\b', '\n'.join(lines)))
        
        if phoenix_mentions > 0 and Phoenix_mentions > 0:
            self.issues.append(StyleIssue(
                line_number=1,
                severity='warning',
                category='Phoenix Terminology',
                message=f"Mixed capitalization: 'phoenix' ({phoenix_mentions}) and 'Phoenix' ({Phoenix_mentions})",
                rule='phoenix_consistency',
                suggestion="Use 'Phoenix' (capitalized) consistently when referring to the tool"
            ))
    
    def _check_content_accessibility(self, lines: List[str]):
        """Check content accessibility and inclusive language"""
        accessibility_config = self.config.get('content_quality', {}).get('accessibility', {})
        
        for line_num, line in enumerate(lines, 1):
            # Check for non-descriptive link text
            link_patterns = ['click here', 'read more', 'see here', 'here', 'this link']
            for pattern in link_patterns:
                if pattern in line.lower() and ('<a' in line or 'href' in line):
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='warning',
                        category='Content Quality',
                        message=f"Non-descriptive link text: '{pattern}'",
                        rule='descriptive_links',
                        suggestion="Use descriptive link text that explains what the link leads to"
                    ))
            
            # Check for ability-neutral language violations
            ability_terms = ['see the image', 'look at', 'as you can see', 'obviously', 'clearly']
            for term in ability_terms:
                if term in line.lower():
                    self.issues.append(StyleIssue(
                        line_number=line_num,
                        severity='info',
                        category='Content Quality',
                        message=f"Consider ability-neutral alternative to '{term}'",
                        rule='ability_neutral',
                        suggestion="Use inclusive language that doesn't assume specific abilities: 'the image shows' instead of 'see the image'"
                    ))
        
        # Check for proper alt text mentions for images
        content_text = '\n'.join(lines)
        image_tags = re.findall(r'<img[^>]*>', content_text, re.IGNORECASE)
        
        for img_tag in image_tags:
            if 'alt=' not in img_tag.lower():
                self.issues.append(StyleIssue(
                    line_number=1,
                    severity='warning',
                    category='Content Quality',
                    message="Image missing alt text for accessibility",
                    rule='image_alt_text',
                    suggestion="Add descriptive alt text to all images for screen reader accessibility"
                ))
    
    def _find_text_in_tree(self, root: ET.Element, text: str) -> bool:
        """Find text content in XML tree"""
        if root.text and text.lower() in root.text.lower():
            return True
        for child in root:
            if self._find_text_in_tree(child, text):
                return True
        return False
    
    def _find_toc_macro(self, root: ET.Element) -> bool:
        """Find table of contents macro"""
        for elem in root.iter():
            # Check both with and without namespace
            if (elem.tag.endswith('structured-macro') and 
                (elem.get('ac:name') == 'toc' or 
                 elem.get('{http://www.atlassian.com/schema/confluence/4/ac/}name') == 'toc')):
                return True
        return False
    
    def _count_callouts(self, root: ET.Element, callout_type: str) -> int:
        """Count specific type of callouts"""
        count = 0
        for elem in root.iter():
            # Check both with and without namespace
            if (elem.tag.endswith('structured-macro') and 
                (elem.get('ac:name') == callout_type or 
                 elem.get('{http://www.atlassian.com/schema/confluence/4/ac/}name') == callout_type)):
                count += 1
        return count

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Nutanix Documentation Style Checker",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📝 Nutanix Documentation Style Checker")
    st.markdown("*Check your XML documentation against official Nutanix style guidelines*")
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 Nutanix Style Guide")
        st.markdown("""
        This tool checks your content against:
        
        **📝 Grammar & Mechanics**
        - Sentence case for headings
        - Active voice and imperative mood
        - Oxford comma usage
        - Proper hyphenation and quotes
        
        **🏷️ Terminology**
        - Correct product names and acronyms
        - Abbreviation rules (define on first use)
        - Approved phrasing for sensitive actions
        - Deprecated term replacement
        
        **💬 Language Quality**
        - Contractions used sparingly
        - Direct address with "you"
        - Parallel structure in lists
        - Appropriate sentence length
        
        **🔧 Technical Standards**
        - Monospace formatting for commands
        - Proper file path formatting
        - Code commenting best practices
        """)
        
        st.header("🎯 Severity Levels")
        st.markdown("""
        - 🚨 **Error**: Critical issues
        - ⚠️ **Warning**: Important fixes needed
        - ℹ️ **Info**: Suggestions for improvement
        """)
    
    # Initialize style checker
    checker = StreamlitStyleChecker()
    
    if not checker.config:
        st.error("Could not load style guide configuration. Please ensure .styleguide.yaml is present.")
        return
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 XML Content Input")
        xml_content = st.text_area(
            "Paste your HTML/XML content here:",
            height=500,
            placeholder="""Paste your HTML or XML documentation content here...

Example HTML:
<h1>How To Resolve an Alert for a CVM That is Low on Memory</h1>
<p>This guide shows you how to troubleshoot memory issues.</p>
<h2>Prerequisites</h2>
<p>Before you begin, ensure the following:</p>
<ul>
  <li>You have access to Prism Element</li>
  <li>You can SSH to the CVM</li>
  <li>You have reviewed KB-1234 for background information</li>
</ul>

Example Confluence XML:
<ac:layout>
  <ac:layout-section ac:type="single">
    <ac:layout-cell>
      <h1>Overview</h1>
      <p>This section provides an overview of the process.</p>
      <ac:structured-macro ac:name="info">
        <ac:parameter ac:name="title">What You Will Learn</ac:parameter>
        <ac:rich-text-body>
          <p>By the end of this section, you'll understand how to...</p>
        </ac:rich-text-body>
      </ac:structured-macro>
    </ac:layout-cell>
  </ac:layout-section>
</ac:layout>

Or plain text:
This is a sample paragraph. Use "you" instead of "the end user".
""",
            help="Paste HTML, XML, or plain text content. The app extracts text from markup and checks it against the Nutanix style guide."
        )
        
        # Check button
        if st.button("🔍 Check Style", type="primary", use_container_width=True):
            if xml_content.strip():
                with st.spinner("Analyzing your content..."):
                    issues = checker.check_content(xml_content)
                    # Generate auto-fixes for applicable issues
                    auto_fixes = checker.fixer.generate_fixes(xml_content, issues)
                    
                st.session_state['issues'] = issues
                st.session_state['auto_fixes'] = auto_fixes
                st.session_state['original_content'] = xml_content
                st.session_state['content_checked'] = True
            else:
                st.warning("Please paste some XML content to check.")
    
    with col2:
        st.header("📊 Style Check Results")
        
        if 'issues' in st.session_state and st.session_state.get('content_checked', False):
            issues = st.session_state['issues']
            auto_fixes = st.session_state.get('auto_fixes', [])
            
            if not issues:
                st.success("🎉 **Excellent!** No style issues found!")
                st.balloons()
            else:
                # Summary metrics with auto-fix info
                errors = [i for i in issues if i.severity == 'error']
                warnings = [i for i in issues if i.severity == 'warning']
                infos = [i for i in issues if i.severity == 'info']
                fixable_issues = [i for i in issues if i.can_auto_fix]
                
                col2a, col2b, col2c, col2d = st.columns(4)
                with col2a:
                    st.metric("🚨 Errors", len(errors))
                with col2b:
                    st.metric("⚠️ Warnings", len(warnings))
                with col2c:
                    st.metric("ℹ️ Info", len(infos))
                with col2d:
                    st.metric("🔧 Auto-fixable", len(fixable_issues))
                
                # Auto-fix section
                if auto_fixes:
                    st.markdown("---")
                    st.subheader("⚡ Quick Fixes Available")
                    
                    # Bulk fix options
                    col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
                    with col_bulk1:
                        if st.button("🔧 Apply All High-Confidence Fixes", use_container_width=True):
                            high_confidence_fixes = [f for f in auto_fixes if f.confidence == 'high']
                            if high_confidence_fixes:
                                fixed_content = checker.fixer.apply_fixes(st.session_state['original_content'], high_confidence_fixes)
                                st.session_state['fixed_content'] = fixed_content
                                st.session_state['applied_fixes'] = high_confidence_fixes
                                st.success(f"✅ Applied {len(high_confidence_fixes)} high-confidence fixes!")
                    
                    with col_bulk2:
                        if st.button("🔧 Apply All Fixes", use_container_width=True):
                            fixed_content = checker.fixer.apply_fixes(st.session_state['original_content'], auto_fixes)
                            st.session_state['fixed_content'] = fixed_content
                            st.session_state['applied_fixes'] = auto_fixes
                            st.success(f"✅ Applied {len(auto_fixes)} fixes!")
                    
                    with col_bulk3:
                        if st.button("👀 Preview Fixes", use_container_width=True):
                            st.session_state['show_preview'] = True
                
                st.markdown("---")
                
                # Display issues by severity with individual fix buttons
                for severity, icon in [('error', '🚨'), ('warning', '⚠️'), ('info', 'ℹ️')]:
                    severity_issues = [i for i in issues if i.severity == severity]
                    if severity_issues:
                        st.subheader(f"{icon} {severity.title()}s ({len(severity_issues)})")
                        
                        for i, issue in enumerate(severity_issues):
                            with st.expander(f"Line {issue.line_number}: {issue.message}"):
                                col_info, col_fix = st.columns([3, 1])
                                
                                with col_info:
                                    st.markdown(f"**Category:** {issue.category}")
                                    st.markdown(f"**Rule:** `{issue.rule}`")
                                    if issue.suggestion:
                                        st.markdown(f"**💡 Suggestion:** {issue.suggestion}")
                                    if issue.original_text:
                                        st.markdown(f"**📝 Found:** `{issue.original_text}`")
                                
                                with col_fix:
                                    if issue.can_auto_fix:
                                        # Find the corresponding auto-fix
                                        fix = next((f for f in auto_fixes if f.line_number == issue.line_number), None)
                                        if fix:
                                            st.markdown(f"**🔧 Fix:** `{fix.fixed_text}`")
                                            st.markdown(f"**Confidence:** {fix.confidence}")
                                            
                                            fix_key = f"fix_{severity}_{i}"
                                            if st.button(f"Apply Fix", key=fix_key, use_container_width=True):
                                                fixed_content = checker.fixer.apply_fixes(st.session_state['original_content'], [fix])
                                                st.session_state['fixed_content'] = fixed_content
                                                st.session_state['applied_fixes'] = [fix]
                                                st.success("✅ Fix applied!")
                                    else:
                                        st.info("Manual fix required")
                
                # Show fixed content if available
                if 'fixed_content' in st.session_state:
                    st.markdown("---")
                    st.subheader("✨ Fixed Content")
                    st.text_area(
                        "Your content with fixes applied:",
                        value=st.session_state['fixed_content'],
                        height=300,
                        help="Copy this fixed content back to your document"
                    )
                    
                    # Show what was fixed
                    applied_fixes = st.session_state.get('applied_fixes', [])
                    if applied_fixes:
                        st.markdown("**🔧 Applied Fixes:**")
                        for fix in applied_fixes:
                            st.write(f"• Line {fix.line_number}: {fix.description}")
                
                # Show preview if requested
                if st.session_state.get('show_preview', False):
                    st.markdown("---")
                    st.subheader("👀 Fix Preview")
                    
                    for fix in auto_fixes:
                        st.markdown(f"**Line {fix.line_number}** ({fix.confidence} confidence):")
                        col_before, col_after = st.columns(2)
                        with col_before:
                            st.markdown("**Before:**")
                            st.code(fix.original_text)
                        with col_after:
                            st.markdown("**After:**")
                            st.code(fix.fixed_text)
                        st.markdown(f"*{fix.description}*")
                        st.markdown("---")
                
                # Download report option
                st.markdown("---")
                if st.button("📥 Download Report", use_container_width=True):
                    report = generate_report(issues)
                    st.download_button(
                        label="Download Style Report",
                        data=report,
                        file_name="style_check_report.txt",
                        mime="text/plain"
                    )
        else:
            st.info("👆 Paste your XML content and click 'Check Style' to see results here.")
    
    # Additional information
    st.markdown("---")
    st.markdown("""
    ### 📚 Need Help?
    
    - **Style Guidelines**: Check the sidebar for an overview of what gets checked
    - **Configuration**: The style rules are defined in `.styleguide.yaml`
    - **Documentation**: See the README.md for detailed information about all style rules
    
    This tool helps ensure your documentation meets Nutanix quality standards for:
    - Technical Publications guidelines
    - KB content guidelines  
    - Training module standards
    - Phoenix-specific terminology
    """)

def generate_report(issues: List[StyleIssue]) -> str:
    """Generate a downloadable text report"""
    report = []
    report.append("NUTANIX DOCUMENTATION STYLE CHECK REPORT")
    report.append("=" * 50)
    report.append("")
    
    # Summary
    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']
    infos = [i for i in issues if i.severity == 'info']
    
    report.append(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
    report.append("")
    
    # Issues by severity
    for severity, icon in [('error', '🚨'), ('warning', '⚠️'), ('info', 'ℹ️')]:
        severity_issues = [i for i in issues if i.severity == severity]
        if severity_issues:
            report.append(f"{icon} {severity.upper()}S:")
            report.append("")
            
            for issue in severity_issues:
                report.append(f"  Line {issue.line_number}: {issue.message}")
                report.append(f"    Category: {issue.category}")
                report.append(f"    Rule: {issue.rule}")
                if issue.suggestion:
                    report.append(f"    Suggestion: {issue.suggestion}")
                report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    main()