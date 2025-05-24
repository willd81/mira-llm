"""
Factory pattern for creating the appropriate scraper based on URL and classification.
"""
from scrapers.sources.html_scraper import HTMLScraper
from scrapers.sources.pdf_scraper import PDFScraper
from scrapers.sources.embedded_scraper import EmbeddedScraper
from scrapers.sources.nsw_playwright_scraper import NSWPlaywrightScraper
from scrapers.sources.qld_playwright_scraper import QLDPlaywrightScraper
from scrapers.sources.wa_playwright_scraper import WAPlaywrightScraper

class ScraperFactory:
    """Factory class for creating appropriate scrapers based on content type."""
    
    @staticmethod
    def create_scraper(url, region, subregion, category, classification):
        """
        Create the appropriate scraper instance.
        
        Args:
            url (str): URL to scrape
            region (str): Region (e.g., "australia", "international")
            subregion (str): Subregion (e.g., "nsw", "qld")
            category (str): Content category
            classification (str): Content classification (pdf, embedded, etc.)
            
        Returns:
            BaseScraper: An instance of the appropriate scraper
        """
        if classification == "pdf":
            return PDFScraper(url, region, subregion, category)
        elif classification == "embedded":
            return EmbeddedScraper(url, region, subregion, category)
        elif classification == "nsw_bulletin_page":
            return NSWPlaywrightScraper(url, region, subregion, category)
        elif classification == "qld_safety_notices":
            return QLDPlaywrightScraper(url, region, subregion, category)
        elif classification == "wa_bulletin_page":
            return WAPlaywrightScraper(url, region, subregion, category)
        else:  # Default to standard HTML
            return HTMLScraper(url, region, subregion, category)
    
    @staticmethod
    def classify_url(url, content_type=""):
        """
        Classify a URL based on its properties and content type.
        
        Args:
            url (str): URL to classify
            content_type (str): Optional content type hint
            
        Returns:
            str: Classification (pdf, embedded, html, etc.)
        """
        content_type = content_type.lower()
        
        # PDF detection
        if url.endswith(".pdf"):
            return "pdf"
            
        # NSW bulletin detection
        if "resourcesregulator.nsw.gov.au" in url and "safety-alerts" in url:
            return "nsw_bulletin_page"
            
        # QLD safety notices detection
        if "rshq.qld.gov.au" in url and "safety-notices" in url:
            return "qld_safety_notices"
            
        # WA bulletin detection
        if "dmp.wa.gov.au" in url and "safety-bulletins" in url:
            return "wa_bulletin_page"
            
        # Embedded content detection
        if "embedded" in content_type:
            return "embedded"
            
        # Default to HTML for long-form content
        return "long_html_article" 