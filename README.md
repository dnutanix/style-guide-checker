# Nutanix Documentation Style Checker

A web-based tool to check your HTML/XML documentation against the Nutanix style guide for consistent, professional writing.

## 🚀 Quick Start

### Run the Style Checker

```bash
# Make the script executable (first time only)
chmod +x run_streamlit_app.sh

# Start the web app
./run_streamlit_app.sh
```

This will:
- Set up a Python virtual environment
- Install required dependencies
- Launch the web interface at http://localhost:8501

### How to Use

1. **Open the web app** in your browser
2. **Paste your content** - HTML, XML, or plain text
3. **Click "Check Style"** to analyze your content
4. **Review the results** - organized by severity (Error/Warning/Info)
5. **Apply suggestions** to improve your documentation

## 📝 What Gets Checked

### Grammar & Mechanics
- **Sentence case** for headings (not Title Case)
- **Active voice** instead of passive voice
- **Oxford comma** usage in lists
- **Proper hyphenation** in compound adjectives (single-node cluster)
- **Double quotes** for UI text and file names

### Terminology 
- **Product names** - Nutanix AOS, Nutanix AHV, etc.
- **Acronym definitions** - Define on first use (Controller VM (CVM))
- **Approved phrasing** for sensitive actions
- **Deprecated terms** - Replace old terms with current ones
- **Technical formatting** - Monospace for commands and processes

### Language Quality
- **Contractions** used sparingly (avoid "should've", "could've")
- **Direct address** with "you" instead of "the end user"
- **Parallel structure** in lists
- **Appropriate length** for sentences and paragraphs

### Content Structure
- **Heading hierarchy** - No skipping levels (h1 → h2 → h3)
- **Table of Contents** for longer documents
- **Proper callouts** for warnings and information

## 🎯 Severity Levels

The checker categorizes issues by importance:

- **🚨 Error** - Critical issues that should be fixed immediately
- **⚠️ Warning** - Important improvements that enhance readability  
- **ℹ️ Info** - Suggestions for better style and consistency

## 💡 Example Issues and Fixes

### Grammar & Mechanics
```
❌ "How To Configure The CVM Settings"
✅ "How to configure the CVM settings"
(Use sentence case for headings)

❌ "The service is restarted by the system"
✅ "The system restarts the service"
(Use active voice)

❌ "This affects AHV, ESXi and Hyper-V"
✅ "This affects AHV, ESXi, and Hyper-V"
(Always use Oxford comma)
```

### Terminology
```
❌ "web console"
✅ "Prism Element"
(Use current product names)

❌ "Use NCC to check the cluster"
✅ "Use Nutanix Cluster Check (NCC) to check the cluster"
(Define acronyms on first use)

❌ "The node is down"
✅ "The node is unresponsive or unavailable"
(Use calm, precise language)
```

### Language Quality
```
❌ "You should've checked the logs"
✅ "You should have checked the logs"
(Avoid ambiguous contractions)

❌ "The end user can customize settings"
✅ "You can customize settings"
(Use direct address)
```

## 🔧 Supported Content Types

The checker handles multiple content formats:

- **Plain text** - Regular documentation text
- **HTML** - Standard HTML with headings, paragraphs, lists
- **XML** - Including Confluence XML with namespaces
- **Mixed content** - HTML/XML with embedded text

### Example Supported Formats

**HTML:**
```html
<h1>How to resolve memory alerts</h1>
<p>This guide shows you how to troubleshoot CVM memory issues.</p>
<ul>
  <li>Check the memory usage</li>
  <li>Review the logs</li>
</ul>
```

**Confluence XML:**
```xml
<ac:layout>
  <ac:layout-section ac:type="single">
    <ac:layout-cell>
      <h1>Overview</h1>
      <p>This section provides an overview.</p>
    </ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

## ⚙️ Configuration

The style rules are defined in `.styleguide.yaml`. This file contains:

- **Grammar rules** - Capitalization, voice, punctuation
- **Terminology standards** - Product names, acronyms, deprecated terms
- **Formatting guidelines** - Code formatting, quotes, hyphens
- **Content quality** - Approved phrasing, sensitive language

You can modify the rules by editing this file, though the default settings follow official Nutanix style guidelines.

## 🆘 Need Help?

### Common Issues

**Import/Installation Errors:**
```bash
# Try installing dependencies manually
pip install streamlit pyyaml
```

**Permission Errors:**
```bash
# Make the script executable
chmod +x run_streamlit_app.sh
```

**Browser Not Opening:**
- Manually go to http://localhost:8501
- Check that port 8501 is available

### Getting Better Results

1. **Start with errors** - Fix critical issues first
2. **Check headings** - Ensure proper sentence case
3. **Review terminology** - Use current Nutanix product names
4. **Focus on clarity** - Use active voice and direct address

### Style Guide Resources

This tool implements the official Nutanix style guidelines:
- Grammar and mechanics standards
- Approved terminology and product names  
- Technical writing best practices
- Accessibility and inclusive language guidelines

For detailed style guidance, refer to the internal Nutanix style documentation.