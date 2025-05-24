"""
PDF downloader for direct PDF links.
"""
import os
import requests
import json
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from scrapers.utils.base_scraper import BaseScraper

class PDFScraper(BaseScraper):
    """Scraper for PDF files from direct PDF links."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize PDF scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
    
    def process(self):
        """Download the PDF file and save metadata."""
        try:
            response = requests.get(self.url, stream=True, timeout=15, headers=self.HEADERS)
            response.raise_for_status()

            # Parse clean filename
            parsed = urlparse(self.url)
            filename = os.path.basename(parsed.path)
            if not filename.endswith(".pdf"):
                filename = "document.pdf"
            
            # Save the PDF file
            filepath = self.save_file(filename, response.content, mode="wb")
            
            # Save metadata
            metadata = {
                "name": filename,
                "url": self.url,
                "region": self.region,
                "subregion": self.subregion,
                "category": self.category,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with open(self.output_path / "metadata.json", "w", encoding="utf-8") as mf:
                json.dump(metadata, mf, indent=2)
                
            print(f"[PDFScraper] Saved PDF: {filepath}")
            return True
            
        except Exception as e:
            print(f"[PDFScraper] Failed to download {self.url}: {e}")
            return False 