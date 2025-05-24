#!/usr/bin/env python
"""
Initialization script to verify the environment is properly set up for the MIRA LLM pipeline.
"""
import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_dependency(package_name):
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def create_directory_structure():
    """Create the necessary directory structure."""
    directories = [
        "data/raw",
        "data/cleaned",
        "logs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_sample_config():
    """Check if the config file exists and create a sample if not."""
    config_path = Path("scraper/config/config.yaml")
    
    if not config_path.exists():
        config_dir = config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a minimal sample config
        sample_config = """
project_name: "MIRA Mining LLM"
description: "Scraper config for mining-related documents."

sources:
  australia:
    nsw:
      - name: "NSW Resources Regulator - Sample"
        url: "https://www.resources.nsw.gov.au/"
        type: "Government Mining Regs"

categories:
  - Government Mining Regs
  - Safety Bulletins & Alerts

output:
  raw_data_dir: "data/raw"
  cleaned_data_dir: "data/cleaned"
"""
        with open(config_path, "w") as f:
            f.write(sample_config)
        print(f"✅ Created sample config file: {config_path}")
    else:
        print(f"✅ Config file exists: {config_path}")

def check_playwright():
    """Check if Playwright is installed and install browsers if needed."""
    if not check_dependency("playwright"):
        print("⚠️ Playwright not installed. Install with: pip install playwright")
        return False
    
    try:
        subprocess.run(["playwright", "install", "chromium"], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        print("✅ Playwright browsers installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Failed to install Playwright browsers. Run: playwright install chromium")
        return False

def main():
    """Main entry point for the initialization script."""
    print("🔄 Initializing MIRA Mining LLM Pipeline...\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"🐍 Python Version: {python_version}")
    
    # Create directory structure
    create_directory_structure()
    
    # Check dependencies
    dependencies = [
        "bs4",            # BeautifulSoup
        "yaml",           # PyYAML
        "requests",       # Requests
        "fitz",           # PyMuPDF
    ]
    
    print("\n📦 Checking dependencies...")
    all_deps_installed = True
    for dep in dependencies:
        if check_dependency(dep):
            print(f"✅ {dep}")
        else:
            print(f"❌ {dep} - Not installed")
            all_deps_installed = False
    
    # Check Playwright
    print("\n🎭 Checking Playwright...")
    check_playwright()
    
    # Check config file
    print("\n📄 Checking configuration...")
    check_sample_config()
    
    print("\n🔎 Environment check complete!")
    
    if not all_deps_installed:
        print("\n⚠️ Some dependencies are missing. Install with: pip install -r requirements.txt")
    else:
        print("\n✅ All basic dependencies are installed!")
        print("\n🚀 You're all set! Try running the pipeline with: python -m pipeline.run_pipeline --scrape-only")

if __name__ == "__main__":
    main() 