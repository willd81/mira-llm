"""
Script to run legislation scraping for all regions with enhanced logging.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from scrapers.sources.legislation_scraper import LegislationScraper
from scrapers.utils.scrape_logger import ScrapeLogger

async def run_legislation_scraping(regions: List[str]) -> Dict:
    """
    Run legislation scraping for specified regions.
    
    Args:
        regions: List of region codes (nsw, qld, wa)
        
    Returns:
        Dict containing scraping statistics
    """
    logger = ScrapeLogger()
    stats = {
        "start_time": datetime.now().isoformat(),
        "regions": {},
        "total_documents": 0,
        "total_errors": 0
    }
    
    for region in regions:
        try:
            print(f"\nProcessing {region.upper()} legislation...")
            scraper = LegislationScraper(region)
            success = await scraper.run()
            
            # Get region statistics
            region_stats = logger.get_region_summary(region)
            stats["regions"][region] = {
                "success": success,
                "documents_downloaded": region_stats["total_downloads"],
                "errors": region_stats["total_errors"]
            }
            
            # Update totals
            stats["total_documents"] += region_stats["total_downloads"]
            stats["total_errors"] += region_stats["total_errors"]
            
            print(f"{region.upper()} legislation scraping {'succeeded' if success else 'failed'}")
            print(f"Documents downloaded: {region_stats['total_downloads']}")
            print(f"Errors encountered: {region_stats['total_errors']}")
            
        except Exception as e:
            print(f"Error scraping {region} legislation: {e}")
            stats["regions"][region] = {
                "success": False,
                "error": str(e)
            }
            stats["total_errors"] += 1
    
    stats["end_time"] = datetime.now().isoformat()
    return stats

async def generate_scraping_report(stats: Dict):
    """Generate a detailed scraping report."""
    report_path = Path("scripts/legislation_scrape_report.json")
    
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    print("\n=== Legislation Scraping Report ===")
    print(f"Total documents downloaded: {stats['total_documents']}")
    print(f"Total errors encountered: {stats['total_errors']}")
    print("\nPer-region statistics:")
    
    for region, region_stats in stats["regions"].items():
        print(f"\n{region.upper()}:")
        if region_stats.get("success") is not None:
            print(f"Success: {region_stats['success']}")
            if region_stats['success']:
                print(f"Documents downloaded: {region_stats['documents_downloaded']}")
                print(f"Errors encountered: {region_stats['errors']}")
        if "error" in region_stats:
            print(f"Error: {region_stats['error']}")
    
    print(f"\nDetailed report saved to: {report_path}")

async def main():
    """Main entry point for legislation scraping."""
    print("Starting MIRA-LLM Legislation Collection Process")
    print("=" * 50)
    
    regions = ["nsw", "qld", "wa"]
    
    try:
        # Run legislation scraping
        stats = await run_legislation_scraping(regions)
        
        # Generate report
        await generate_scraping_report(stats)
        
        # Return success if any documents were downloaded
        return stats["total_documents"] > 0
        
    except Exception as e:
        print(f"\nError in legislation scraping process: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 