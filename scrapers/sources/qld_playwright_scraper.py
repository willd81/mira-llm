"""
Specialized scraper for QLD RSHQ safety notices using Playwright.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from scrapers.utils.base_scraper import BaseScraper

class QLDPlaywrightScraper(BaseScraper):
    """Specialized scraper for QLD RSHQ safety notices using Playwright."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize QLD scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
        
    async def fetch_page_content(self):
        """Fetch page content using Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                # Wait for the content to load
                await page.wait_for_selector(".search-results", timeout=10000)
                
                # Select all industries to show all notices
                await page.click("text=Select all")
                await page.wait_for_timeout(1000)
                
                # Click search button
                await page.click("text=Search Safety and Health Alerts")
                await page.wait_for_timeout(2000)
                
                # Click "Load more" until no more results
                while True:
                    try:
                        load_more = await page.query_selector("text=Load more")
                        if not load_more:
                            break
                        await load_more.click()
                        await page.wait_for_timeout(1000)  # Wait for content
                    except Exception:
                        break
                
                content = await page.content()
                await browser.close()
                return content
            except Exception as e:
                print(f"[QLDPlaywrightScraper] Error fetching page: {e}")
                await browser.close()
                return None
    
    async def extract_and_download_notices(self):
        """Extract and download safety notices."""
        html = await self.fetch_page_content()
        if not html:
            return
            
        print("[QLDPlaywrightScraper] Page content loaded")
        soup = BeautifulSoup(html, "html.parser")
        notices = []
        
        # Find all notice entries
        for notice in soup.select(".search-results .notice-item"):
            try:
                title = notice.select_one("h3").text.strip()
                industry = notice.select_one(".industry").text.strip()
                subject = notice.select_one(".subject").text.strip()
                link = notice.select_one("a")["href"]
                
                notice_data = {
                    "title": title,
                    "industry": industry,
                    "subject": subject,
                    "url": urljoin(self.url, link)
                }
                notices.append(notice_data)
            except Exception as e:
                print(f"[QLDPlaywrightScraper] Error parsing notice: {e}")
        
        # Save notice metadata
        metadata_path = self.output_path / "notices_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(notices, f, indent=2)
        
        # Download each notice
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            for notice in notices:
                try:
                    await page.goto(notice["url"], timeout=60000)
                    content = await page.content()
                    
                    # Create filename from title
                    safe_title = "".join(c if c.isalnum() else "_" for c in notice["title"])
                    filename = f"{safe_title[:50]}.html"
                    
                    # Save the notice content
                    path = self.output_path / filename
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[QLDPlaywrightScraper] Saved: {filename}")
                    
                except Exception as e:
                    print(f"[QLDPlaywrightScraper] Failed to fetch notice: {notice['url']} — {e}")
            
            await browser.close()
    
    def process(self):
        """Process the URL using Playwright to handle dynamic content."""
        print("[QLDPlaywrightScraper] Launching crawler...")
        asyncio.run(self.extract_and_download_notices())
        return True 