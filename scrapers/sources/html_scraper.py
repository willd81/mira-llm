"""
HTML content scraper for standard web pages.
"""
from bs4 import BeautifulSoup
from scrapers.utils.base_scraper import BaseScraper

class HTMLScraper(BaseScraper):
    """Scraper for standard HTML content pages."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize HTML scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
    
    def process(self):
        """Process the URL, extract HTML content, and save."""
        html = self.fetch_url()
        if html:
            self.save_file("content.html", html)
            print(f"[HTMLScraper] Saved content from {self.url}")
            return True
        return False 