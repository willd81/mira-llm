"""
NSW-specific Playwright-based scraper for NSW government bulletins.
"""
import asyncio
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from scrapers.utils.base_scraper import BaseScraper

class NSWPlaywrightScraper(BaseScraper):
    """Specialized scraper for NSW government safety bulletins using Playwright."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize NSW Playwright scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
        self.output_path = Path(f"data/raw/{self.region}/{self.subregion}/bulletins")
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    async def fetch_page_content(self):
        """Fetch page content using Playwright for dynamic content."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print(f"[NSWPlaywrightScraper] Navigating to: {self.url}")
            await page.goto(self.url, timeout=60000)
            await page.wait_for_timeout(5000)
            await page.screenshot(path=str(self.output_path / "debug_screenshot.png"))
            content = await page.content()
            await browser.close()
            return content
    
    async def extract_and_download_links(self):
        """Extract and download links from the page using Playwright."""
        html = await self.fetch_page_content()
        print("[NSWPlaywrightScraper] Page content loaded")
        soup = BeautifulSoup(html, "html.parser")
        links = []

        print("[NSWPlaywrightScraper] All hrefs found:")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            print(" -", href)
            if ".pdf" in href.lower() or "/safety-alerts/" in href:
                full_url = urljoin(self.url, href)
                links.append(full_url)

        if not links:
            print("[NSWPlaywrightScraper] No valid bulletin links found")
            return

        links = list(set(links))
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            for i, link in enumerate(links):
                try:
                    await page.goto(link, timeout=60000)
                    content = await page.content()
                    filename = link.split("/")[-1].split("?")[0] or f"page_{i}.html"
                    if not filename.endswith(".pdf"):
                        filename += ".html"
                    path = self.output_path / filename
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[NSWPlaywrightScraper] Saved: {filename}")
                except Exception as e:
                    print(f"[NSWPlaywrightScraper] Failed to fetch: {link} — {e}")
            await browser.close()
    
    def process(self):
        """Process the URL using Playwright to handle dynamic content."""
        print("[NSWPlaywrightScraper] Launching crawler...")
        asyncio.run(self.extract_and_download_links())
        return True 