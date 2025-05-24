"""
Specialized scraper for mining legislation documents.
"""
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from scrapers.config.scraper_config import (
    DOCUMENT_CATEGORIES,
    DOCUMENT_SELECTORS,
    FILE_TYPES,
    METADATA_FIELDS,
    REGION_URLS,
    SCRAPER_CONFIG
)
from scrapers.utils.base_scraper import BaseScraper

class LegislationScraper(BaseScraper):
    """Specialized scraper for mining legislation documents."""
    
    def __init__(self, region: str):
        """Initialize legislation scraper."""
        super().__init__(
            base_url=REGION_URLS[region]["legislation"],
            region=region,
            category="legislation",
            doc_type="all"
        )
        self.processed_urls: Set[str] = set()
        self.stats = {
            "documents_processed": 0,
            "documents_downloaded": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat()
        }
        self.selectors = DOCUMENT_SELECTORS[region]
    
    async def setup_playwright(self):
        """Set up Playwright browser for dynamic content."""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch()
        context = await browser.new_context(
            viewport=SCRAPER_CONFIG["playwright"]["viewport"],
            user_agent=SCRAPER_CONFIG["user_agent"]
        )
        page = await context.new_page()
        return playwright, browser, context, page
    
    async def cleanup_playwright(self, playwright, browser, context, page):
        """Clean up Playwright resources."""
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
    
    async def wait_for_content(self, page) -> bool:
        """Wait for content to load on dynamic pages."""
        try:
            for selector in SCRAPER_CONFIG["playwright"]["wait_for"]["selectors"]:
                try:
                    await page.wait_for_selector(
                        selector,
                        timeout=SCRAPER_CONFIG["playwright"]["wait_for"]["timeout"]
                    )
                    return True
                except PlaywrightTimeout:
                    continue
            
            # Try content selectors as fallback
            for selector in self.selectors["content"].split(", "):
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    return True
                except PlaywrightTimeout:
                    continue
            
            return False
        except Exception as e:
            self.logger.log_error(
                self.region,
                page.url,
                f"Error waiting for content: {str(e)}",
                "content_wait_error"
            )
            return False
    
    async def download_document(self, url: str, session: aiohttp.ClientSession) -> Tuple[bool, Optional[str]]:
        """Download a document with proper binary handling."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.log_error(
                        self.region,
                        url,
                        f"Failed to download document: HTTP {response.status}",
                        "download_error"
                    )
                    return False, None
                
                # Get content type and filename
                content_type = response.headers.get("content-type", "")
                content_disp = response.headers.get("content-disposition", "")
                
                # Try to get filename from content disposition
                filename = None
                if content_disp:
                    match = re.search(r'filename="?([^"]+)"?', content_disp)
                    if match:
                        filename = match.group(1)
                
                if not filename:
                    filename = url.split("/")[-1]
                    if not any(filename.lower().endswith(ext) for ext in FILE_TYPES):
                        filename += ".pdf"
                
                # Ensure safe filename
                safe_filename = "".join(c if c.isalnum() or c in ".-_" else "_" for c in filename)
                file_path = self.output_dir / safe_filename
                
                # Download in binary mode
                content = await response.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                self.stats["documents_downloaded"] += 1
                return True, safe_filename
                
        except Exception as e:
            self.logger.log_error(
                self.region,
                url,
                f"Error downloading document: {str(e)}",
                "download_error"
            )
            return False, None
    
    async def process_document_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and process document links from page."""
        document_links = []
        
        # Process PDF links
        for link in soup.select(self.selectors["pdf_links"]):
            href = link.get("href")
            if href and href not in self.processed_urls:
                full_url = urljoin(base_url, href)
                document_links.append(full_url)
                self.processed_urls.add(href)
        
        # Process DOC links
        for link in soup.select(self.selectors["doc_links"]):
            href = link.get("href")
            if href and href not in self.processed_urls:
                full_url = urljoin(base_url, href)
                document_links.append(full_url)
                self.processed_urls.add(href)
        
        return document_links
    
    async def scrape_with_playwright(self, url: str) -> List[str]:
        """Scrape page using Playwright for dynamic content."""
        playwright, browser, context, page = await self.setup_playwright()
        try:
            await page.goto(url, timeout=SCRAPER_CONFIG["timeout"])
            content_loaded = await self.wait_for_content(page)
            
            if not content_loaded:
                self.logger.log_error(
                    self.region,
                    url,
                    "Failed to load dynamic content",
                    "content_load_error"
                )
                return []
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            return await self.process_document_links(soup, url)
            
        except Exception as e:
            self.logger.log_error(
                self.region,
                url,
                f"Playwright scraping error: {str(e)}",
                "playwright_error"
            )
            return []
            
        finally:
            await self.cleanup_playwright(playwright, browser, context, page)
    
    async def scrape_with_aiohttp(self, url: str) -> List[str]:
        """Scrape page using aiohttp for static content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.logger.log_error(
                            self.region,
                            url,
                            f"Failed to fetch page: HTTP {response.status}",
                            "http_error"
                        )
                        return []
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return await self.process_document_links(soup, url)
                    
        except Exception as e:
            self.logger.log_error(
                self.region,
                url,
                f"Aiohttp scraping error: {str(e)}",
                "aiohttp_error"
            )
            return []
    
    async def process_url(self, url: str) -> bool:
        """Process a URL and download all relevant documents."""
        # Try aiohttp first
        document_links = await self.scrape_with_aiohttp(url)
        
        # If no documents found, try Playwright
        if not document_links:
            document_links = await self.scrape_with_playwright(url)
        
        if not document_links:
            self.logger.log_error(
                self.region,
                url,
                "No document links found",
                "no_documents_error"
            )
            return False
        
        # Download documents
        async with aiohttp.ClientSession() as session:
            download_tasks = [
                self.download_document(link, session)
                for link in document_links
            ]
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Count successful downloads
            successful_downloads = sum(1 for result in results if isinstance(result, tuple) and result[0])
            
            return successful_downloads >= SCRAPER_CONFIG["minimum_documents_required"]
    
    async def run(self) -> bool:
        """Run the legislation scraper for the configured region."""
        try:
            # Process main legislation page
            success = await self.process_url(self.base_url)
            
            # Process codes of practice if available
            if "codes" in REGION_URLS[self.region]:
                codes_success = await self.process_url(REGION_URLS[self.region]["codes"])
                success = success or codes_success
            
            self.stats["end_time"] = datetime.now().isoformat()
            
            # Only return true if we downloaded the minimum required documents
            return success and self.stats["documents_downloaded"] >= SCRAPER_CONFIG["minimum_documents_required"]
            
        except Exception as e:
            self.logger.log_error(
                self.region,
                self.base_url,
                f"Error in legislation scraper: {str(e)}",
                "scraper_error"
            )
            self.stats["errors"] += 1
            self.stats["end_time"] = datetime.now().isoformat()
            return False
    
    def get_stats(self) -> Dict:
        """Get scraping statistics."""
        return self.stats

def main():
    """Main entry point for legislation scraping."""
    asyncio.run(LegislationScraper.scrape_all_regions()) 