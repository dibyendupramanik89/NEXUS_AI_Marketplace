#!/usr/bin/env python3
"""
Script to convert ARCHITECTURE.html to PNG format using multiple methods
"""
import subprocess
import sys
from pathlib import Path

def convert_with_puppeteer():
    """Try using node-based solution"""
    try:
        import os
        html_file = Path(__file__).parent / "ARCHITECTURE.html"
        output_file = Path(__file__).parent / "ARCHITECTURE_DIAGRAM.png"
        
        # Try wkhtmltopdf (cross-platform)
        result = subprocess.run(
            ["wkhtmltoimage", str(html_file), str(output_file)],
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0 and output_file.exists():
            print(f"✅ Architecture diagram saved to: {output_file}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return False

def convert_with_playwright():
    """Use playwright if available"""
    try:
        import asyncio
        from playwright.async_api import async_playwright
        
        async def convert():
            html_file = Path(__file__).parent / "ARCHITECTURE.html"
            output_file = Path(__file__).parent / "ARCHITECTURE_DIAGRAM.png"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={"width": 1400, "height": 1200})
                await page.goto(f"file://{html_file.absolute()}")
                await page.screenshot(path=str(output_file), full_page=True)
                await browser.close()
            
            print(f"✅ Architecture diagram saved to: {output_file}")
            return True
        
        return asyncio.run(convert())
    except Exception as e:
        print(f"⚠️  Playwright conversion failed: {e}")
        return False

def create_svg_version():
    """Create SVG version as fallback"""
    html_file = Path(__file__).parent / "ARCHITECTURE.html"
    svg_file = Path(__file__).parent / "ARCHITECTURE_DIAGRAM.svg"
    
    # Read the HTML and save as reference
    with open(html_file, 'r') as f:
        html_content = f.read()
    
    # Create an SVG wrapper (simplified)
    svg_content = f"""<svg width="1400" height="1200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            {html_content.split('<style>')[1].split('</style>')[0]}
        </style>
    </defs>
    <rect width="1400" height="1200" fill="white"/>
    <text x="700" y="50" font-size="28" font-weight="bold" text-anchor="middle" fill="#1a1a1a">
        NEXUS Enterprise Agentic AI Platform
    </text>
    <text x="700" y="80" font-size="14" text-anchor="middle" fill="#0066cc">
        Secure · Observable · Governed · Scalable
    </text>
</svg>"""
    
    with open(svg_file, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ SVG version created at: {svg_file}")
    return True

if __name__ == "__main__":
    html_file = Path(__file__).parent / "ARCHITECTURE.html"
    
    if not html_file.exists():
        print(f"❌ {html_file} not found!")
        sys.exit(1)
    
    print("🚀 Converting ARCHITECTURE.html to PNG...\n")
    
    # Try methods in order
    if convert_with_puppeteer():
        sys.exit(0)
    
    if convert_with_playwright():
        sys.exit(0)
    
    # Fallback to SVG
    print("\n⚠️  Using SVG fallback (install wkhtmltoimage or playwright for PNG)")
    if create_svg_version():
        print("📝 HTML file is also available at: ARCHITECTURE.html")
        print("\n💡 To generate PNG, install: pip install playwright")
        sys.exit(0)
    
    print("❌ Conversion failed!")
    sys.exit(1)

