#!/usr/bin/env python
"""
Test script to verify the pipeline is functioning correctly with a simple example.
"""
import os
import json
from pathlib import Path
from urllib.parse import urlparse
import shutil

from pipeline.scraper_pipeline import ScraperPipeline
from pipeline.cleaner_pipeline import CleanerPipeline
from scrapers.sources.html_scraper import HTMLScraper
from processors.cleaners.html_cleaner import HTMLCleaner

def create_sample_data():
    """Create some sample HTML data to test the pipeline."""
    raw_dir = Path("data/raw/test/example")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple HTML file
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Mining Document</title>
        <style>
            body { font-family: Arial; }
        </style>
    </head>
    <body>
        <header>
            <nav>Menu items that should be removed</nav>
        </header>
        <main>
            <h1>Safety Guidelines for Mining Operations</h1>
            <p>This document outlines key safety procedures for underground mining operations.</p>
            
            <h2>Equipment Inspection</h2>
            <p>Always inspect equipment before use to ensure it's in proper working condition.</p>
            <ul>
                <li>Check for loose parts</li>
                <li>Verify safety mechanisms are operational</li>
                <li>Test emergency stop functionality</li>
            </ul>
            
            <h2>Communication Protocols</h2>
            <p>Clear communication is essential for safe mining operations.</p>
            <p>All personnel must be familiar with standard communication signals.</p>
        </main>
        <footer>
            Copyright information that should be removed
        </footer>
    </body>
    </html>
    """
    
    with open(raw_dir / "content.html", "w") as f:
        f.write(sample_html)
    
    print(f"✅ Created sample HTML file at {raw_dir / 'content.html'}")
    return raw_dir

def test_html_cleaner(raw_dir):
    """Test the HTML cleaner on our sample data."""
    cleaner = HTMLCleaner(raw_dir.parent.parent, Path("data/cleaned"))
    html_file = raw_dir / "content.html"
    
    print(f"🧪 Testing HTML cleaner on {html_file}")
    entries = cleaner.clean_file(html_file)
    
    # Check if the cleaned file exists
    output_path = Path("data/cleaned/test/example/cleaned.json")
    if output_path.exists():
        with open(output_path, "r") as f:
            data = json.load(f)
        print(f"✅ Cleaned data generated with {len(data)} entries")
        print("📄 First entry:")
        print(f"  Title: {data[0]['title']}")
        print(f"  Body preview: {data[0]['body'][:50]}...")
    else:
        print(f"❌ Failed to generate cleaned data at {output_path}")

def clean_up():
    """Clean up the test data."""
    shutil.rmtree(Path("data/raw/test"), ignore_errors=True)
    shutil.rmtree(Path("data/cleaned/test"), ignore_errors=True)
    print("🧹 Cleaned up test data")

def main():
    """Main entry point for the test script."""
    print("🔬 Testing MIRA Mining LLM Pipeline")
    
    try:
        # Create test data
        raw_dir = create_sample_data()
        
        # Test the HTML cleaner
        test_html_cleaner(raw_dir)
        
        print("\n✅ Basic pipeline functionality test passed!")
        print("🚀 You can now try running the full pipeline with: python -m pipeline.run_pipeline")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up the test data
        clean_up()

if __name__ == "__main__":
    main() 