"""
Configuration for document scrapers.
"""
from typing import Dict, List

# Document categories and their subdirectories
DOCUMENT_CATEGORIES = {
    "legislation": ["acts", "regulations", "codes"],
    "safety_alerts": ["bulletins", "alerts", "notices"],
    "guidance": ["guidelines", "standards", "procedures"],
    "sops": ["procedures", "protocols", "standards"]
}

# Base URLs for different regions
REGION_URLS = {
    "nsw": {
        "base": "https://www.resourcesregulator.nsw.gov.au",
        "legislation": "https://www.resourcesregulator.nsw.gov.au/safety/mining-legislation",
        "safety_alerts": "https://www.resourcesregulator.nsw.gov.au/safety-alerts",
        "guidance": "/guidance-and-resources",
        "codes": "https://www.safework.nsw.gov.au/legal-obligations/codes-of-practice"
    },
    "qld": {
        "base": "https://www.business.qld.gov.au",
        "legislation": "https://www.business.qld.gov.au/industries/mining-energy-water/resources/safety-health/mining/legislation",
        "safety_alerts": "https://www.rshq.qld.gov.au/safety-notices/mines",
        "guidance": "/guidance-materials",
        "codes": "https://www.business.qld.gov.au/industries/mining-energy-water/resources/safety-health/mining/legislation-standards/recognised-standards"
    },
    "wa": {
        "base": "https://www.dmp.wa.gov.au",
        "legislation": "https://www.dmp.wa.gov.au/Safety/Safety-legislation-standards-5957.aspx",
        "safety_alerts": "https://www.dmp.wa.gov.au/Safety/Mines-safety-alerts-13194.aspx",
        "guidance": "/guidance-and-resources",
        "codes": "https://www.commerce.wa.gov.au/worksafe/codes-practice"
    }
}

# File types to scrape
FILE_TYPES = [".pdf", ".doc", ".docx", ".rtf"]

# Metadata fields to extract
METADATA_FIELDS = [
    "title",
    "date_published",
    "document_type",
    "region",
    "category",
    "url",
    "filename"
]

# Scraper configuration
SCRAPER_CONFIG = {
    "timeout": 20000,  # milliseconds
    "retry_attempts": 3,
    "delay_between_retries": 3,  # seconds
    "minimum_documents_required": 1,
    "max_concurrent_requests": 5,
    "user_agent": "Mining-Safety-Document-Collector/1.0",
    "playwright": {
        "viewport": {"width": 1920, "height": 1080},
        "wait_for": {
            "selectors": ["a[href$='.pdf']", "a[href$='.doc']", "a[href$='.docx']"],
            "timeout": 30000  # milliseconds
        }
    }
}

# Document selectors for different regions
DOCUMENT_SELECTORS = {
    "nsw": {
        "pdf_links": "a[href$='.pdf']",
        "doc_links": "a[href$='.doc'], a[href$='.docx']",
        "content": "main, #content, .content"
    },
    "qld": {
        "pdf_links": ".document-list a[href$='.pdf']",
        "doc_links": ".document-list a[href$='.doc'], .document-list a[href$='.docx']",
        "content": "#main-content, .main-content"
    },
    "wa": {
        "pdf_links": ".document-container a[href$='.pdf']",
        "doc_links": ".document-container a[href$='.doc'], .document-container a[href$='.docx']",
        "content": "#main, .main-content"
    }
}

# Pagination patterns for different sites
PAGINATION_PATTERNS = {
    "nsw": {"param": "page", "start": 1},
    "qld": {"param": "p", "start": 1},
    "wa": {"param": "page", "start": 1}
} 