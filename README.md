# Nutanix Documentation Style Checker

A comprehensive automated style checking system that enforces consistency and quality standards across all documentation files based on official Nutanix guidelines.

## 🎯 Purpose

This system automatically checks your documentation against multiple official Nutanix style guidelines to ensure:

- **Consistency** across all documentation files and training modules
- **Quality** adherence to professional writing standards from Tech-Pubs
- **Technical accuracy** in KB references, version numbers, and Phoenix terminology
- **Training compliance** with Nutanix training module standards and PII guidelines
- **Content organization** proper use of callouts, warnings, and expandable sections
- **Accessibility** compliance with inclusive language and accessibility guidelines
- **Brand compliance** with Nutanix style, terminology, and approved resources

## 🚀 Quick Start

### Option 1: Web Interface (Recommended for Quick Checks)

Run the Streamlit web app for an easy-to-use interface:

```bash
./run_streamlit_app.sh
```

This will:
- Set up a Python virtual environment
- Install required dependencies
- Launch a web interface at http://localhost:8501

**Features of the Web App:**
- 📝 **Paste & Check**: Simply paste your XML content and get instant feedback
- 🎯 **Real-time Analysis**: See issues categorized by severity (Error/Warning/Info)
- 💡 **Suggestions**: Get specific recommendations for each issue
- 📊 **Visual Dashboard**: Clean interface with metrics and progress indicators
- 📥 **Download Reports**: Export your style check results

### Option 2: Command Line (For Automated Workflows)

#### 1. Setup (One-time)

Run the setup script to install the style checker:

```bash
./setup-style-checker.sh
```

This script will:
- Install required Python dependencies
- Set up the Git pre-commit hook
- Test the style checker on existing files

#### 2. Usage

The style checker runs automatically on every Git commit, but you can also run it manually:

```bash
# Check all XML files
./style-checker.py

# Check specific files
./style-checker.py chapter1.xml chapter2.xml

# Different output formats
./style-checker.py --format json
./style-checker.py --format text

# Filter by severity
./style-checker.py --severity error    # Only show errors
./style-checker.py --severity warning  # Show errors and warnings
./style-checker.py --severity info     # Show everything
```

## 📋 What Gets Checked

### Document Structure & Organization
- ✅ **Chapter Structure**: Required sections (Overview, What You Will Learn)
- ✅ **Table of Contents**: Placement and formatting requirements
- ✅ **Content Organization**: Info callouts, warning callouts, tip callouts, expandable sections
- ✅ **Navigation**: Proper linking standards and descriptive text

### Content Quality & Accuracy
- ✅ **Article Types**: Break-fix vs generic troubleshooting classification
- ✅ **Visibility Levels**: Public, customer, partner, and internal content guidelines
- ✅ **KB References**: Proper formatting (KB-####) and linking requirements
- ✅ **Version Numbers**: Consistent formatting (X.Y.Z pattern)
- ✅ **Safety Warnings**: Required for data loss operations, cluster impact actions
- ✅ **Technical Accuracy**: Version consistency, command syntax validation
- ✅ **Prohibited Content**: PII, negative terms, non-inclusive language
- ✅ **Standard Disclaimers**: Required disclaimers for workaround articles

### Writing Standards (Tech-Pubs Guidelines)
- ✅ **Fundamental Principles**: Clear communication priority, guidelines flexibility
- ✅ **Grammar Standards**: 
  - Simple present tense (avoid complex tenses and contractions)
  - Active voice (subject performs action, avoid passive voice)
  - Direct address (use "you", avoid "the end user")
- ✅ **Language Clarity**: 
  - Ability-neutral language, avoid jargon and metaphors
  - Specific terminology fixes (use "IP address" not "IP")
  - Avoid anthropomorphic language ("cluster thinks")
  - Inclusive language requirements
- ⚠️ **Style Resources**: Adherence to approved style guides (Microsoft, IBM, Chicago Manual)

### Training-Specific Standards
- ✅ **Module Naming**: Proper conventions for init.SRE, Level 1-3 modules
- ✅ **Subpage Naming**: Topic_Name format with proper navigation links
- ✅ **Table of Contents**: Required for all training modules and subpages
- ✅ **Layout Requirements**: Template usage, content alignment, required sections
- ✅ **Image Guidelines**: Highlight clicks, borders required, direct upload only
- ✅ **Code Block Standards**: Django theme, Plain Text syntax, proper setup process
- ✅ **Command Formatting**: Blue color and monospace font for inline commands
- ✅ **Menu Items**: Bold text formatting requirement
- ✅ **PII Guidelines**: Prohibited content, acceptable generalizations, image blurring

### Formatting & Code Standards
- ✅ **Text Formatting**: 
  - Default fonts, no colored text, double quotes in sentences
  - File paths in italics, GUI paths with ">" separator
  - Proper emphasis (strong, em, code) usage
- ⚠️ **List Standards**: Numbered for instructions, bullets for unordered info
- ⚠️ **Table Standards**: Avoid nested tables, no size constraints
- ✅ **Code Formatting**: 
  - Proper command prompts, inline vs block usage
  - File path formatting, Phoenix-specific terminology
- ⚠️ **Inline Styles**: Discourages excessive inline styling

### Media & Image Standards
- ✅ **Image Requirements**: Alt text for accessibility, standard web formats
- ✅ **Training Images**: Screenshot highlighting, borders, upload methods
- ✅ **KB Images**: Convert CLI to text, complement GUI errors with text
- ⚠️ **PII in Images**: Redaction required, blurring tools, prohibited content

### Phoenix-Specific Content
- ✅ **Terminology Consistency**: Proper Phoenix, CVM, AOS, AHV usage
- ✅ **Phoenix Terms**: Phoenix Installer, Rescue Shell, Phoenix Shell, Installer Menu
- ✅ **Procedures**: ISO creation, installer navigation, troubleshooting approaches

## 🔧 Configuration

### Style Guide Configuration (`.styleguide.yaml`)

The main configuration file defines all style rules organized into major sections:

```yaml
# Document structure for content organization
document_structure:
  chapter_structure:
    required_sections:
      - "Overview"
    recommended_sections:
      - "What You Will Learn"

# Content organization and callouts
content_organization:
  callout_usage:
    info_callouts:
      purpose: "Chapter overviews, tips, helpful context"
    warning_callouts:
      purpose: "Critical safety information, data loss warnings"

# Content quality standards from official guidelines
content_quality:
  article_structure:
    article_types:
      break_fix: "Issues tied to specific product/feature"
      generic_troubleshooting: "Non-issue-focused workflow guidance"
  content_visibility:
    visibility_levels:
      public: "Indexable by search engines"
      customer: "Requires Portal authentication"
      internal: "Nutanix employees only"

# Writing standards from Tech-Pubs Guidelines
writing_standards:
  fundamental_principles:
    primary_goal: "communicate_clearly"
  grammar:
    verb_tense: "simple_present"
    voice: "active"
    person: "second"

# Training-specific standards
training_standards:
  module_naming:
    init_sre: "Module_Name - init.SRE"
    level_1: "Module_Name - Level 1"
  pii_guidelines:
    prohibited_content:
      - "Names or email addresses"
      - "IP Addresses, Serial Numbers"

# And much more...
```

### Git Hook Configuration

The pre-commit hook automatically runs on every commit. You can modify `.git/hooks/pre-commit` to:

- Change severity levels that block commits
- Modify output format
- Skip certain file types
- Customize error messages

### Excluding Files

To exclude specific files or patterns from checking, edit `.styleguide.yaml`:

```yaml
exclusions:
  excluded_files:
    - "legacy-*.xml"
    - "temp/*.xml"
```

## 📊 Severity Levels

- **🚨 ERROR**: Critical issues that block Git commits
  - Missing required XML elements
  - Invalid XML structure
  - Broken KB links (when validation enabled)

- **⚠️ WARNING**: Important issues that allow commits but should be fixed
  - Discouraged inline styles
  - Missing KB links
  - Inconsistent formatting

- **ℹ️ INFO**: Suggestions for improvement
  - Missing Table of Contents
  - Version format inconsistencies
  - Style recommendations

## 🎨 Example Output

```
📋 Style Check Report
==================================================

🚨 ERRORS:

  chapter3-creating-a-phoenix-iso.xml:15
    Missing required element: ac:layout-cell
    Rule: required_elements

⚠️  WARNINGS:

  chapter5-install-or-repair-cvm.xml:42
    Discouraged inline style: letter-spacing: 0.0px
    Rule: inline_styles

  chapter4-running-the-installer.xml:156
    KB reference KB-5013 should be linked
    Rule: kb_links

ℹ️  INFO:

  chapter2-basics-of-phoenix.xml:1
    Table of Contents not found
    Rule: toc_recommended

==================================================
Summary: 1 errors, 2 warnings, 1 info
```

## 🔄 Git Integration

### Automatic Checking

The pre-commit hook automatically runs style checks on XML files before each commit:

```bash
git add chapter1.xml
git commit -m "Update chapter 1"

# Style checker runs automatically
🔍 Running TC Phoenix Documentation Style Checker...
📝 Checking files:
  - chapter1.xml

🔍 Running style checks...
✅ All style checks passed!
```

### Bypassing Checks (Not Recommended)

In rare cases where you need to commit despite style issues:

```bash
git commit --no-verify -m "Emergency fix"
```

**⚠️ Warning**: Only use `--no-verify` for urgent fixes. Always return to fix style issues afterward.

## 🛠️ Customization

### Adding New Rules

1. **Edit `.styleguide.yaml`**: Add your rule configuration
2. **Update `style-checker.py`**: Implement the checking logic
3. **Test**: Run the checker on sample files
4. **Document**: Update this README with the new rule

### Example: Adding a New Rule

```yaml
# In .styleguide.yaml
custom_rules:
  phoenix_terminology:
    preferred_terms:
      - old: "Nutanix cluster"
        new: "cluster"
        reason: "Redundant - cluster implies Nutanix"
```

```python
# In style-checker.py
def _check_terminology(self, line, line_number):
    """Check for preferred terminology"""
    terminology = self.config.get('custom_rules', {}).get('phoenix_terminology', {})
    # Implementation here...
```

## 🐛 Troubleshooting

### Common Issues

**"PyYAML not installed"**
```bash
pip3 install PyYAML
# or
python3 -m pip install --user PyYAML
```

**"Pre-commit hook not executing"**
```bash
chmod +x .git/hooks/pre-commit
```

**"XML parsing errors"**
- Check for unmatched tags
- Ensure proper Confluence namespace usage
- Validate XML structure

**"Too many style violations"**
- Start with `--severity error` to fix critical issues first
- Use `--format json` for programmatic processing
- Fix issues incrementally

### Getting Help

1. **Check the configuration**: Review `.styleguide.yaml` for rule details
2. **Run with verbose output**: Use `--severity info` to see all issues
3. **Test specific rules**: Create minimal test files to isolate issues
4. **Check logs**: Review pre-commit hook output for detailed error messages

## 📚 Style Guide References

This system implements comprehensive style guidelines from multiple official sources:

### Primary Style Guidelines
- **Nutanix Technical Publications Writing Guidelines**
  - Simple present tense, active voice, direct address ("you")
  - Clear communication priority, guidelines flexibility
  - Approved style resources (Microsoft, IBM, Chicago Manual of Style)

- **Nutanix KB Content Style Guidelines**
  - Article types (break-fix vs generic troubleshooting)
  - Content visibility levels (public, customer, partner, internal)
  - Prohibited content (PII, negative terms, non-inclusive language)
  - Text formatting, lists, tables, and image standards

- **Nutanix Training Guidelines**
  - Module naming conventions (init.SRE, Level 1-3)
  - Table of Contents requirements for all modules
  - Code block standards (Django theme, Plain Text syntax)
  - PII guidelines and acceptable generalizations
  - Image requirements (borders, direct upload, click highlighting)

### Supporting Style Resources
- **Microsoft Style Guide** (technical writing standards)
- **IBM Style Guide** (technical documentation)
- **Chicago Manual of Style** (general style and grammar)
- **Global English Style Guide by John R. Kohl** (international accessibility)
- **Web Content Accessibility Guidelines (WCAG)** (accessibility compliance)
- **Nutanix Brand Guidelines** (brand consistency)
- **Nutanix Inclusive Language Guidelines** (inclusive terminology)

### Internal References
- **Nutanix Glossary** (approved terminology)
- **Acronyms Reference** (first-use rules)
- **Considerations Taxonomy** (content classification)
- **TC Phoenix Internal Style Conventions** (project-specific standards)

## 🔮 Future Enhancements

Planned improvements for the style checker:

### Content Validation
- [ ] **Link validation**: Check that all URLs are accessible
- [ ] **KB reference validation**: Verify KB links point to valid articles
- [ ] **Cross-reference validation**: Ensure internal links are valid
- [ ] **Version number validation**: Check against current product versions

### Language & Style Checking
- [ ] **Grammar checking**: Advanced grammar validation beyond basic rules
- [ ] **Spell checking**: Integration with technical dictionaries and Nutanix glossary
- [ ] **Terminology consistency**: Auto-detect preferred terms from Nutanix Glossary
- [ ] **Inclusive language detection**: Advanced detection of non-inclusive terms

### Training-Specific Features
- [ ] **Module template validation**: Ensure proper use of training templates
- [ ] **PII detection**: Automated detection of personal identifiable information
- [ ] **Command prompt validation**: Verify acceptable generalized formats
- [ ] **Code block theme enforcement**: Ensure Django theme usage

### Technical Features
- [ ] **Image alt-text checking**: Validate accessibility of images
- [ ] **Performance optimization**: Faster checking for large repositories
- [ ] **Batch processing**: Parallel processing of multiple files
- [ ] **Incremental checking**: Only check modified content

### Integration & Tooling
- [x] **Streamlit Web Interface**: User-friendly web app for paste-and-check functionality
- [ ] **VS Code extension**: Real-time style checking in editor
- [ ] **CI/CD integration**: Automated checking in build pipelines
- [ ] **Confluence integration**: Direct validation of published content
- [ ] **Metrics dashboard**: Track style compliance over time

## 🤝 Contributing

To contribute improvements to the style checker:

1. **Test your changes** on existing documentation
2. **Update the configuration** in `.styleguide.yaml`
3. **Document new rules** in this README
4. **Ensure backward compatibility** with existing documents

## 📄 License

This style checker is part of the TC Phoenix documentation project and follows the same licensing terms as the rest of the project.