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
from typing import List, Dict, Tuple
from dataclasses import dataclass
import io

@dataclass
class StyleIssue:
    """Represents a style guide violation"""
    line_number: int
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    rule: str
    suggestion: str = ""

class StreamlitStyleChecker:
    """Streamlit-specific style checker class"""
    
    def __init__(self, config_path: str = ".styleguide.yaml"):
        self.config = self._load_config(config_path)
        self.issues: List[StyleIssue] = []
        
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
            
        lines = content.split('\n')
        
        # Focus on content checking based on .styleguide.yaml
        self._check_content_lines(lines)
        
        # Check for document structure patterns (content-based, not XML structure)
        self._check_document_content_structure(lines)
        
        return self.issues
    
    def _check_document_content_structure(self, lines: List[str]):
        """Check document structure based on content patterns"""
        content_text = '\n'.join(lines).lower()
        
        # Check for required sections based on content
        doc_structure = self.config.get('document_structure', {})
        chapter_structure = doc_structure.get('chapter_structure', {})
        
        required_sections = chapter_structure.get('required_sections', [])
        for section in required_sections:
            if section.lower() not in content_text:
                self.issues.append(StyleIssue(
                    line_number=1,
                    severity='info',
                    category='Document Structure',
                    message=f"Consider adding a '{section}' section",
                    rule='document_structure',
                    suggestion=f"Documents typically benefit from having a '{section}' section to introduce the content"
                ))
        
        # Check for table of contents mention
        if 'table of contents' not in content_text and len(lines) > 50:
            self.issues.append(StyleIssue(
                line_number=1,
                severity='info',
                category='Document Structure',
                message="Long document without Table of Contents",
                rule='table_of_contents',
                suggestion="Consider adding a Table of Contents for documents with multiple sections"
            ))
    
    def _check_content_lines(self, lines: List[str]):
        """Check content line by line against all style guidelines"""
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and XML tags for content checking
            if not line.strip() or (line.strip().startswith('<') and line.strip().endswith('>')):
                continue
                
            # Check all major style guideline categories
            self._check_writing_standards(line, line_num)
            self._check_content_quality(line, line_num)
            self._check_formatting_standards(line, line_num)
            self._check_training_standards(line, line_num)
            self._check_technical_content(line, line_num)
        
        # Check multi-line patterns
        self._check_multi_line_patterns(lines)
        
        # Check for specific multi-line content patterns
        self._check_document_patterns(lines)
        
        # Check content accessibility
        self._check_content_accessibility(lines)
    
    def _check_writing_standards(self, line: str, line_num: int):
        """Check writing standards from Tech-Pubs guidelines"""
        writing_standards = self.config.get('writing_standards', {})
        grammar = writing_standards.get('grammar', {})
        language_clarity = writing_standards.get('language_clarity', {})
        
        # Check for passive voice indicators
        passive_indicators = ['is set', 'are set', 'was set', 'were set', 'is monitored', 'are monitored', 
                            'is performed', 'are performed', 'is created', 'are created']
        for indicator in passive_indicators:
            if indicator in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Writing Standards',
                    message=f"Passive voice detected: '{indicator}'",
                    rule='active_voice',
                    suggestion="Rewrite in active voice (subject performs action). Example: 'SCMA resets the component' instead of 'The component is reset by SCMA'"
                ))
        
        # Check for contractions (Tech-Pubs guideline)
        contractions = ["won't", "don't", "can't", "shouldn't", "couldn't", "wouldn't", "isn't", "aren't"]
        for contraction in contractions:
            if contraction in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Writing Standards',
                    message=f"Contraction found: '{contraction}'",
                    rule='avoid_contractions',
                    suggestion=f"Use full form instead: {contraction} → {self._expand_contraction(contraction)}"
                ))
        
        # Check for third-person references (should use "you")
        third_person_refs = ["the end user", "the user", "the customer", "users can", "customers can"]
        for ref in third_person_refs:
            if ref in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Writing Standards',
                    message=f"Third-person reference: '{ref}'",
                    rule='direct_address',
                    suggestion="Use 'you' to address the reader directly (Tech-Pubs guideline)"
                ))
        
        # Check for prohibited terms from language clarity guidelines
        avoid_terms = language_clarity.get('terminology_fixes', {}).get('avoid_terms', [])
        for term_rule in avoid_terms:
            if isinstance(term_rule, str) and term_rule.lower() in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Writing Standards',
                    message=f"Consider more specific term than '{term_rule}'",
                    rule='terminology_clarity',
                    suggestion=f"Use more specific language (e.g., 'IP address' instead of 'IP')"
                ))
        
        # Check for anthropomorphic language
        anthropomorphic = ["cluster thinks", "cluster needs", "cluster searches", "system wants", "software decides"]
        for phrase in anthropomorphic:
            if phrase in line.lower():
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Writing Standards',
                    message=f"Anthropomorphic language: '{phrase}'",
                    rule='avoid_anthropomorphism',
                    suggestion="Define the process or requirements instead of attributing human characteristics to systems"
                ))
    
    def _expand_contraction(self, contraction: str) -> str:
        """Expand contractions to full forms"""
        expansions = {
            "won't": "will not", "don't": "do not", "can't": "cannot",
            "shouldn't": "should not", "couldn't": "could not", "wouldn't": "would not",
            "isn't": "is not", "aren't": "are not"
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
        """Check technical content standards"""
        technical_content = self.config.get('technical_content', {})
        
        # Check KB references formatting
        kb_config = technical_content.get('kb_references', {})
        kb_pattern = r'KB-?\d+'
        matches = re.findall(kb_pattern, line, re.IGNORECASE)
        
        for match in matches:
            if not re.match(r'KB-\d+', match):
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='warning',
                    category='Technical Content',
                    message=f"KB reference format issue: '{match}'",
                    rule='kb_references',
                    suggestion="Use format 'KB-####' (e.g., KB-5013)"
                ))
            
            # Check if KB reference should be linked
            if match in line and '<a' not in line:
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Technical Content',
                    message=f"KB reference '{match}' should be linked",
                    rule='kb_links',
                    suggestion="Add a link to the KB article on the Nutanix Portal"
                ))
        
        # Check version number consistency
        version_config = technical_content.get('version_numbers', {})
        version_pattern = r'\b\d+\.\d+(?:\.\d+)?\b'
        matches = re.findall(version_pattern, line)
        
        for match in matches:
            if len(match.split('.')) == 2:
                self.issues.append(StyleIssue(
                    line_number=line_num,
                    severity='info',
                    category='Technical Content',
                    message=f"Version number '{match}' might benefit from full X.Y.Z format",
                    rule='version_numbers',
                    suggestion="Consider using three-part version numbers (e.g., 7.3.0 instead of 7.3)"
                ))
        
        # Check for proper Phoenix terminology
        if re.search(r'\bphoenix\b', line.lower()) and 'Phoenix' not in line:
            self.issues.append(StyleIssue(
                line_number=line_num,
                severity='info',
                category='Technical Content',
                message="Found lowercase 'phoenix' - should be capitalized",
                rule='phoenix_terminology',
                suggestion="Use 'Phoenix' (capitalized) when referring to the tool"
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
        st.header("📋 Style Guidelines")
        st.markdown("""
        This tool checks your content against:
        
        **✅ Tech-Pubs Guidelines**
        - Simple present tense
        - Active voice
        - Direct address ("you")
        
        **✅ KB Content Guidelines**
        - Proper KB references (KB-####)
        - Content visibility standards
        - Prohibited content (PII, negative terms)
        
        **✅ Training Guidelines**
        - Module naming conventions
        - PII protection
        - Code block standards
        
        **✅ Formatting Standards**
        - Phoenix terminology
        - Version number consistency
        - Image and media guidelines
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
            "Paste your XML content here:",
            height=500,
            placeholder="""Paste your XML documentation content here...

Example (Confluence XML):
<ac:layout>
  <ac:layout-section ac:type="single">
    <ac:layout-cell>
      <h1>Overview</h1>
      <p>This section provides an overview of Phoenix.</p>
      <ac:structured-macro ac:name="info" ac:schema-version="1">
        <ac:parameter ac:name="title">What You Will Learn</ac:parameter>
        <ac:rich-text-body>
          <p>Learning objectives go here...</p>
        </ac:rich-text-body>
      </ac:structured-macro>
    </ac:layout-cell>
  </ac:layout-section>
</ac:layout>

Or simple HTML:
<p>This is a sample paragraph with some content.</p>
<h1>Overview</h1>
<p>Use "you" instead of "the end user" for direct address.</p>
""",
            help="Paste the XML content from your documentation file. The app handles both Confluence XML with namespaces and simple HTML."
        )
        
        # Check button
        if st.button("🔍 Check Style", type="primary", use_container_width=True):
            if xml_content.strip():
                with st.spinner("Analyzing your content..."):
                    issues = checker.check_content(xml_content)
                st.session_state['issues'] = issues
                st.session_state['content_checked'] = True
            else:
                st.warning("Please paste some XML content to check.")
    
    with col2:
        st.header("📊 Style Check Results")
        
        if 'issues' in st.session_state and st.session_state.get('content_checked', False):
            issues = st.session_state['issues']
            
            if not issues:
                st.success("🎉 **Excellent!** No style issues found!")
                st.balloons()
            else:
                # Summary metrics
                errors = [i for i in issues if i.severity == 'error']
                warnings = [i for i in issues if i.severity == 'warning']
                infos = [i for i in issues if i.severity == 'info']
                
                col2a, col2b, col2c = st.columns(3)
                with col2a:
                    st.metric("🚨 Errors", len(errors))
                with col2b:
                    st.metric("⚠️ Warnings", len(warnings))
                with col2c:
                    st.metric("ℹ️ Info", len(infos))
                
                st.markdown("---")
                
                # Display issues by severity
                for severity, icon in [('error', '🚨'), ('warning', '⚠️'), ('info', 'ℹ️')]:
                    severity_issues = [i for i in issues if i.severity == severity]
                    if severity_issues:
                        st.subheader(f"{icon} {severity.title()}s ({len(severity_issues)})")
                        
                        for issue in severity_issues:
                            with st.expander(f"Line {issue.line_number}: {issue.message}"):
                                st.markdown(f"**Category:** {issue.category}")
                                st.markdown(f"**Rule:** `{issue.rule}`")
                                if issue.suggestion:
                                    st.markdown(f"**💡 Suggestion:** {issue.suggestion}")
                
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