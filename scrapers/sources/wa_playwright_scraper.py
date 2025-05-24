"""
Specialized scraper for WA DMIRS safety bulletins using Playwright.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from scrapers.utils.base_scraper import BaseScraper

class WAPlaywrightScraper(BaseScraper):
    """Specialized scraper for WA DMIRS safety bulletins using Playwright."""
    
    def __init__(self, url, region, subregion, category):
        """Initialize WA scraper with the provided parameters."""
        super().__init__(url, region, subregion, category)
        self.old_url = "https://www.dmp.wa.gov.au/Safety/Mines-safety-alerts-13194.aspx"
        self.new_url = "https://worksafe.wa.gov.au/health-and-safety-alerts"
        
    async def fetch_page_content(self, url):
        """Fetch page content using Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=60000)
                # Wait for the content to load
                if "worksafe.wa.gov.au" in url:
                    await page.wait_for_selector(".alert-list", timeout=10000)
                else:
                    await page.wait_for_selector(".bulletin-list", timeout=10000)
                
                content = await page.content()
                await browser.close()
                return content
            except Exception as e:
                print(f"[WAPlaywrightScraper] Error fetching page: {e}")
                await browser.close()
                return None
    
    async def extract_and_download_bulletins(self):
        """Extract and download safety bulletins from both old and new sites."""
        # First try the new site
        html = await self.fetch_page_content(self.new_url)
        if html:
            await self.process_new_site(html)
        
        # Then try the old site
        html = await self.fetch_page_content(self.old_url)
        if html:
            await self.process_old_site(html)
            
    async def process_new_site(self, html):
        """Process alerts from the new WorkSafe WA site."""
        print("[WAPlaywrightScraper] Processing new site content")
        soup = BeautifulSoup(html, "html.parser")
        alerts = []
        
        # Find all alert sections
        for section in soup.select(".alert-section"):
            try:
                title = section.select_one("h2").text.strip()
                date = section.select_one(".date").text.strip()
                category = section.select_one(".category").text.strip()
                link = section.select_one("a")["href"]
                
                alert_data = {
                    "title": title,
                    "date": date,
                    "category": category,
                    "url": urljoin(self.new_url, link)
                }
                alerts.append(alert_data)
            except Exception as e:
                print(f"[WAPlaywrightScraper] Error parsing new site alert: {e}")
        
        # Save alert metadata
        metadata_path = self.output_path / "wa_alerts_new_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
        
        # Download each alert
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            for alert in alerts:
                try:
                    await page.goto(alert["url"], timeout=60000)
                    content = await page.content()
                    
                    # Create filename from date and title
                    date = datetime.strptime(alert["date"], "%d %B %Y")
                    date_str = date.strftime("%Y%m%d")
                    safe_title = "".join(c if c.isalnum() else "_" for c in alert["title"])
                    filename = f"{date_str}_{safe_title[:50]}.html"
                    
                    # Save the alert content
                    path = self.output_path / filename
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[WAPlaywrightScraper] Saved new site alert: {filename}")
                    
                except Exception as e:
                    print(f"[WAPlaywrightScraper] Failed to fetch new site alert: {alert['url']} — {e}")
            
            await browser.close()
            
    async def process_old_site(self, html):
        """Process bulletins from the old DMIRS site."""
        print("[WAPlaywrightScraper] Processing old site content")
        soup = BeautifulSoup(html, "html.parser")
        bulletins = []
        
        # Find all bulletin entries
        for bulletin in soup.select(".bulletin-item"):
            try:
                title = bulletin.select_one(".bulletin-title").text.strip()
                date = bulletin.select_one(".bulletin-date").text.strip()
                category = bulletin.select_one(".bulletin-category").text.strip()
                pdf_link = bulletin.select_one("a[href$='.pdf']")["href"]
                
                bulletin_data = {
                    "title": title,
                    "date": date,
                    "category": category,
                    "url": urljoin(self.old_url, pdf_link)
                }
                bulletins.append(bulletin_data)
            except Exception as e:
                print(f"[WAPlaywrightScraper] Error parsing old site bulletin: {e}")
        
        # Save bulletin metadata
        metadata_path = self.output_path / "wa_bulletins_old_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(bulletins, f, indent=2)
        
        # Download each bulletin PDF
        for bulletin in bulletins:
            try:
                response = self.session.get(bulletin["url"], timeout=30)
                response.raise_for_status()
                
                # Create filename from date and title
                date = datetime.strptime(bulletin["date"], "%d/%m/%Y")
                date_str = date.strftime("%Y%m%d")
                safe_title = "".join(c if c.isalnum() else "_" for c in bulletin["title"])
                filename = f"{date_str}_{safe_title[:50]}.pdf"
                
                # Save the PDF
                path = self.output_path / filename
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"[WAPlaywrightScraper] Saved old site bulletin: {filename}")
                
            except Exception as e:
                print(f"[WAPlaywrightScraper] Failed to download old site PDF: {bulletin['url']} — {e}")
    
    def process(self):
        """Process the URL using Playwright to handle dynamic content."""
        print("[WAPlaywrightScraper] Launching crawler...")
        asyncio.run(self.extract_and_download_bulletins())
        return True 