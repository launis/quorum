#!/usr/bin/env python3
"""
Cognitive Quorum Architecture Documentation - Complete PDF Exporter
Converts markdown with embedded Mermaid diagrams to a professional PDF
"""

import re
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Color output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, level: str = "info"):
    """Print colored status messages"""
    if level == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif level == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif level == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif level == "info":
        print(f"{Colors.CYAN}📖 {message}{Colors.END}")
    else:
        print(f"{Colors.BOLD}{message}{Colors.END}")

def read_markdown_file(file_path: str) -> str:
    """Read the markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print_status(f"File not found: {file_path}", "error")
        sys.exit(1)

def extract_mermaid_diagrams(markdown_text: str) -> dict:
    """Extract all Mermaid diagrams from markdown"""
    pattern = r'```mermaid\n(.*?)```'
    diagrams = {}
    
    for i, match in enumerate(re.finditer(pattern, markdown_text, re.DOTALL)):
        diagram_code = match.group(1).strip()
        diagram_id = f"mermaid_diagram_{i+1}"
        diagrams[diagram_id] = {
            'code': diagram_code,
            'position': match.start(),
            'type': detect_diagram_type(diagram_code)
        }
    
    return diagrams

def detect_diagram_type(diagram_code: str) -> str:
    """Detect the type of Mermaid diagram"""
    first_line = diagram_code.split('\n')[0].lower()
    if 'graph' in first_line or 'flowchart' in first_line:
        return 'flowchart'
    elif 'sequenceDiagram' in diagram_code:
        return 'sequence'
    elif 'classDiagram' in diagram_code:
        return 'class'
    elif 'stateDiagram' in diagram_code:
        return 'state'
    else:
        return 'unknown'

def replace_mermaid_with_placeholders(markdown_text: str, diagrams: dict) -> str:
    """Replace mermaid code blocks with simple text placeholders"""
    modified_text = markdown_text
    
    # Sort diagrams by position (reverse order to maintain positions)
    sorted_diagrams = sorted(diagrams.items(), key=lambda x: x[1]['position'], reverse=True)
    
    for diagram_id, diagram_info in sorted_diagrams:
        # Find and replace mermaid code block
        pattern = r'```mermaid\n' + re.escape(diagram_info['code']) + r'\n```'
        # Simple text placeholder that markdown won't mangle (no underscores)
        safe_id = diagram_id.replace('_', '')
        placeholder = f'MERMAIDPLACEHOLDER{safe_id}'
        modified_text = re.sub(pattern, placeholder, modified_text, count=1)
    
    return modified_text

def inject_mermaid_html(html_content: str, diagrams: dict) -> str:
    """Replace text placeholders with actual mermaid HTML divs after markdown conversion"""
    modified_html = html_content
    for diagram_id, diagram_info in diagrams.items():
        # Escape <, >, & but NOT quotes (" or '), because Mermaid's parser 
        # chokes on &quot; or &#x27; inside node definitions.
        escaped_code = diagram_info['code'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        div_html = f'<div id="{diagram_id}" class="mermaid">\n{escaped_code}\n</div>'
        # Markdown usually wraps the placeholder in <p> tags
        safe_id = diagram_id.replace('_', '')
        ph = f'MERMAIDPLACEHOLDER{safe_id}'
        modified_html = modified_html.replace(f'<p>{ph}</p>', div_html)
        modified_html = modified_html.replace(f'{ph}', div_html)
        
    return modified_html

def markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML"""
    try:
        import markdown2
        html = markdown2.markdown(markdown_text, extras=['tables', 'fenced-code-blocks', 'code-color'])
        return html
    except ImportError:
        print_status("markdown2 not installed. Installing...", "warning")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown2'], check=True)
        import markdown2
        html = markdown2.markdown(markdown_text, extras=['tables', 'fenced-code-blocks', 'code-color'])
        return html

def create_html_template(html_content: str, diagrams: dict) -> str:
    """Create complete HTML template with Mermaid support"""
    
    mermaid_scripts = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'loose', maxTextSize: 90000 });
        });
    </script>
"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cognitive Quorum V2 - Complete Architecture Manual</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #fff;
            padding: 0;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            .page-break {{
                page-break-after: always;
            }}
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px;
        }}
        
        h1 {{
            color: #0066cc;
            border-bottom: 4px solid #00b894;
            padding-bottom: 15px;
            margin: 40px 0 20px 0;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #1e90ff;
            border-left: 4px solid #00b894;
            padding-left: 15px;
            margin: 30px 0 15px 0;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #4a90e2;
            margin: 20px 0 10px 0;
            page-break-after: avoid;
        }}
        
        h4, h5, h6 {{
            color: #2c3e50;
            margin: 15px 0 8px 0;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 12px 0;
            text-align: justify;
        }}
        
        pre {{
            background: #f5f5f5;
            border-left: 4px solid #00b894;
            padding: 15px;
            margin: 15px 0;
            overflow-x: auto;
            border-radius: 4px;
            font-size: 12px;
            page-break-inside: avoid;
        }}
        
        code {{
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 2px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
        }}
        
        pre code {{
            background: transparent;
            padding: 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        th {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        
        tr:nth-child(even) {{
            background: #fafafa;
        }}
        
        blockquote {{
            border-left: 4px solid #00b894;
            padding-left: 15px;
            margin: 15px 0;
            color: #666;
            font-style: italic;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 30px 0;
            background: #fafafa;
            padding: 20px;
            border-radius: 4px;
        }}
        
        .mermaid-placeholder {{
            text-align: center;
            margin: 30px 0;
            background: #fafafa;
            padding: 20px;
            border-radius: 4px;
            min-height: 300px;
            page-break-inside: avoid;
        }}
        
        .page-break {{
            page-break-after: always;
            margin: 40px 0;
            border-top: 2px dashed #ccc;
            padding-top: 40px;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #555;
        }}
        
        .title-page {{
            text-align: center;
            padding: 100px 40px;
            page-break-after: always;
        }}
        
        .title-page h1 {{
            font-size: 48px;
            color: #0066cc;
            margin: 20px 0;
            border: none;
            padding: 0;
        }}
        
        .title-page p {{
            font-size: 18px;
            color: #666;
            margin: 10px 0;
        }}
        
        .toc {{
            page-break-after: always;
        }}
        
        .toc h2 {{
            margin-top: 0;
        }}
        
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        
        .toc a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 40px 0;
            page-break-after: avoid;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>🧠 Cognitive Quorum V2</h1>
        <h2 style="color: #1e90ff; border: none; padding: 0; margin: 10px 0;">Complete Architecture Manual</h2>
        <p style="margin: 30px 0 10px 0;"><strong>Repository:</strong> <a href="https://github.com/launis/quorum">launis/quorum</a></p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p style="margin-top: 50px; color: #999; font-size: 14px;">Multi-agent AI orchestration for auditable skill assessment</p>
    </div>
    
    <div class="container">
        {html_content}
    </div>
    
    {mermaid_scripts}
    
</body>
</html>
"""
    return html_template

def html_to_pdf(html_content: str, output_path: str) -> bool:
    """Convert HTML to PDF using Playwright"""
    try:
        from playwright.async_api import async_playwright
        import asyncio
        
        async def convert():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set viewport for proper rendering
                await page.set_viewport_size({"width": 1200, "height": 800})
                
                # Write HTML to temp file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_html = f.name
                
                try:
                    # Navigate to file
                    await page.goto(f'file://{temp_html}', wait_until='networkidle')
                    
                    # Wait for Mermaid diagrams to render
                    await page.wait_for_timeout(5000)
                    
                    # Generate PDF
                    await page.pdf(
                        path=output_path,
                        format='A4',
                        margin={'top': '20mm', 'right': '20mm', 'bottom': '20mm', 'left': '20mm'},
                        print_background=True,
                        prefer_css_page_size=True
                    )
                    
                    return True
                finally:
                    os.unlink(temp_html)
                    await browser.close()
        
        asyncio.run(convert())
        return True
        
    except ImportError:
        print_status("Playwright not installed. Installing...", "warning")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        return html_to_pdf(html_content, output_path)
    except Exception as e:
        print_status(f"PDF conversion failed: {str(e)}", "error")
        return False

def main():
    """Main export function"""
    print_status("🚀 Cognitive Quorum Architecture PDF Exporter", "")
    print()
    
    # Paths
    script_dir = Path(__file__).parent
    markdown_file = script_dir / "koko_arkkitehtuuri.md"
    export_dir = script_dir.parent.parent / "exports"
    pdf_output = export_dir / "Cognitive_Quorum_Complete_Architecture.pdf"
    
    # Create export directory
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Read markdown
    print_status(f"Reading markdown file: {markdown_file}", "info")
    if not markdown_file.exists():
        print_status(f"File not found: {markdown_file}", "error")
        sys.exit(1)
    
    markdown_text = read_markdown_file(str(markdown_file))
    print_status(f"Read {len(markdown_text)} characters", "success")
    
    # Step 2: Extract Mermaid diagrams
    print_status("Extracting Mermaid diagrams...", "info")
    diagrams = extract_mermaid_diagrams(markdown_text)
    print_status(f"Found {len(diagrams)} diagrams", "success")
    for diagram_id, info in diagrams.items():
        print(f"  • {diagram_id}: {info['type']}")
    
    # Step 3: Replace mermaid blocks with placeholders
    print_status("Preparing markdown with diagram placeholders...", "info")
    modified_markdown = replace_mermaid_with_placeholders(markdown_text, diagrams)
    
    # Step 4: Convert markdown to HTML
    print_status("Converting markdown to HTML...", "info")
    html_content = markdown_to_html(modified_markdown)
    
    # Step 4.5: Inject mermaid HTML
    html_content = inject_mermaid_html(html_content, diagrams)
    print_status("Markdown converted to HTML", "success")
    
    # Step 5: Create HTML template
    print_status("Creating HTML template with Mermaid support...", "info")
    full_html = create_html_template(html_content, diagrams)
    
    # Step 6: Convert to PDF
    print_status("Converting HTML to PDF (this may take a minute)...", "info")
    if html_to_pdf(full_html, str(pdf_output)):
        print_status(f"PDF created successfully: {pdf_output}", "success")
        print()
        print_status(f"File size: {pdf_output.stat().st_size / (1024*1024):.2f} MB", "")
        print()
        print_status("✨ Export complete!", "success")
        print()
        print(f"📄 Open your PDF: {pdf_output}")
    else:
        print_status("PDF conversion failed", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()