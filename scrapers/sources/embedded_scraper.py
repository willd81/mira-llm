"""
Scraper for embedded text content from web pages.
"""
from bs4 import BeautifulSoup
from scrapers.utils.base_scraper import BaseScraper

class EmbeddedScraper(BaseScraper):
    """Scraper for embedded text content from web pages."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize embedded content scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
    
    def process(self):
        """Process the URL, extract embedded text content, and save."""
        html = self.fetch_url()
        if html:
            # Parse the HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
                
            # Get the main content
            main = soup.find("main") or soup.body or soup
            
            # Extract text content
            embedded_text = main.get_text(separator="\n", strip=True)
            
            # Save the extracted text
            self.save_file("embedded.txt", embedded_text)
            print(f"[EmbeddedScraper] Extracted and saved content from {self.url}")
            return True
        return False 