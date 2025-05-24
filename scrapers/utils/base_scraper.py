"""
Base scraper class with common functionality.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from scrapers.utils.scrape_logger import ScrapeLogger

class BaseScraper:
    """Base class for all scrapers with common functionality."""
    
    def __init__(self, base_url: str, region: str, category: str, doc_type: str):
        """Initialize base scraper."""
        self.base_url = base_url
        self.region = region
        self.category = category
        self.doc_type = doc_type
        self.logger = ScrapeLogger()
        
        # Create output directory
        self.output_dir = Path("data/raw") / region / category
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract common metadata from a document page."""
        metadata = {
            "source_url": url,
            "region": self.region,
            "category": self.category,
            "doc_type": self.doc_type,
            "date_collected": datetime.now().isoformat()
        }
        
        # Try to extract title
        title_elem = soup.find(["h1", "h2", "title"])
        if title_elem:
            metadata["title"] = title_elem.text.strip()
        
        # Try to extract date
        date_elem = soup.find(class_=["date", "published-date"])
        if date_elem:
            metadata["date_published"] = date_elem.text.strip()
        
        return metadata
    
    async def download_document(self, url: str, filename: str, metadata: Optional[Dict] = None) -> bool:
        """Download a document and save its metadata."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Save document
                        file_path = self.output_dir / filename
                        content = await response.read()
                        
                        with open(file_path, "wb") as f:
                            f.write(content)
                        
                        # Save metadata
                        if metadata:
                            metadata_path = file_path.with_suffix(".json")
                            with open(metadata_path, "w") as f:
                                json.dump(metadata, f, indent=2)
                        
                        # Log success
                        self.logger.log_document(
                            self.region,
                            self.doc_type,
                            url,
                            True,
                            metadata
                        )
                        return True
                    else:
                        # Log failure
                        self.logger.log_document(
                            self.region,
                            self.doc_type,
                            url,
                            False,
                            {"error": f"HTTP {response.status}"}
                        )
                        return False
                        
        except Exception as e:
            # Log error
            self.logger.log_error(
                self.region,
                url,
                str(e),
                "download_error"
            )
            return False
    
    async def run(self) -> bool:
        """Run the scraper. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run()") 