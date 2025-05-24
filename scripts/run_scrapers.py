"""
Script to run document scrapers for mining safety regulations.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from scrapers.sources.legislation_scraper import LegislationScraper
from scrapers.config.scraper_config import REGION_URLS, SCRAPER_CONFIG
from scrapers.utils.scrape_logger import ScrapeLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/scraper.log")
    ]
)
logger = logging.getLogger(__name__)

async def run_legislation_scraping(regions: List[str]) -> Dict:
    """
    Run legislation scraping for specified regions.
    
    Args:
        regions: List of region codes (nsw, qld, wa)
        
    Returns:
        Dict containing scraping statistics
    """
    stats = {
        "start_time": datetime.now().isoformat(),
        "regions": {},
        "total_documents": 0,
        "total_errors": 0,
        "successful_regions": 0
    }
    
    for region in regions:
        logger.info(f"Starting legislation scraping for {region.upper()}")
        
        try:
            scraper = LegislationScraper(region)
            success = await scraper.run()
            scraper_stats = scraper.get_stats()
            
            stats["regions"][region] = {
                "success": success,
                "documents_downloaded": scraper_stats["documents_downloaded"],
                "errors": scraper_stats["errors"],
                "start_time": scraper_stats["start_time"],
                "end_time": scraper_stats.get("end_time", "")
            }
            
            # Update totals
            stats["total_documents"] += scraper_stats["documents_downloaded"]
            stats["total_errors"] += scraper_stats["errors"]
            if success:
                stats["successful_regions"] += 1
            
            logger.info(f"Completed {region.upper()} scraping:")
            logger.info(f"Success: {success}")
            logger.info(f"Documents downloaded: {scraper_stats['documents_downloaded']}")
            logger.info(f"Errors encountered: {scraper_stats['errors']}")
            
        except Exception as e:
            error_msg = f"Error scraping {region}: {str(e)}"
            logger.error(error_msg)
            stats["regions"][region] = {
                "success": False,
                "error": error_msg,
                "documents_downloaded": 0,
                "errors": 1
            }
            stats["total_errors"] += 1
    
    stats["end_time"] = datetime.now().isoformat()
    return stats

async def generate_scraping_report(stats: Dict):
    """Generate a detailed scraping report."""
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"legislation_scrape_report_{timestamp}.json"
    
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    # Generate summary
    summary = [
        "\n=== Legislation Scraping Report ===",
        f"Total documents downloaded: {stats['total_documents']}",
        f"Total errors encountered: {stats['total_errors']}",
        f"Successful regions: {stats['successful_regions']}/{len(stats['regions'])}",
        "\nPer-region statistics:"
    ]
    
    for region, region_stats in stats["regions"].items():
        summary.extend([
            f"\n{region.upper()}:",
            f"Success: {region_stats['success']}",
            f"Documents downloaded: {region_stats.get('documents_downloaded', 0)}",
            f"Errors encountered: {region_stats.get('errors', 0)}"
        ])
        if "error" in region_stats:
            summary.append(f"Error: {region_stats['error']}")
    
    summary.extend([
        f"\nDetailed report saved to: {report_path}",
        "=" * 40
    ])
    
    logger.info("\n".join(summary))
    
    # Also save summary to a text file
    summary_path = reports_dir / f"legislation_scrape_summary_{timestamp}.txt"
    with open(summary_path, "w") as f:
        f.write("\n".join(summary))

async def main():
    """Main entry point for running scrapers."""
    logger.info("Starting MIRA-LLM Document Collection Process")
    logger.info("=" * 50)
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    
    regions = ["nsw", "qld", "wa"]
    
    try:
        # Run legislation scraping
        stats = await run_legislation_scraping(regions)
        
        # Generate report
        await generate_scraping_report(stats)
        
        # Return success only if we have documents from all regions
        success = all(
            region_stats.get("success", False)
            for region_stats in stats["regions"].values()
        )
        
        if success:
            logger.info("Scraping completed successfully for all regions")
        else:
            logger.warning("Scraping completed with some failures")
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error in scraping process: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(main()) 