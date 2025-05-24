"""
Logger utility for scraping operations.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ScrapeLogger:
    """Logger for scraping operations with audit capabilities."""
    
    def __init__(self, audit_file: str = "scripts/audit_scrape_log.json"):
        """Initialize the scrape logger."""
        self.audit_file = Path(audit_file)
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "documents": [],
            "errors": [],
            "stats": {
                "total_processed": 0,
                "successful": 0,
                "failed": 0
            }
        }
        
        # Load existing audit log or create new one
        if self.audit_file.exists():
            with open(self.audit_file, "r") as f:
                self.audit_log = json.load(f)
        else:
            self.audit_log = {
                "scraping_history": [],
                "document_stats": {
                    "legislation": {
                        "nsw": {"total": 0, "successful": 0, "failed": 0},
                        "qld": {"total": 0, "successful": 0, "failed": 0},
                        "wa": {"total": 0, "successful": 0, "failed": 0}
                    },
                    "safety_alerts": {
                        "nsw": {"total": 0, "successful": 0, "failed": 0},
                        "qld": {"total": 0, "successful": 0, "failed": 0},
                        "wa": {"total": 0, "successful": 0, "failed": 0}
                    },
                    "guidance": {
                        "nsw": {"total": 0, "successful": 0, "failed": 0},
                        "qld": {"total": 0, "successful": 0, "failed": 0},
                        "wa": {"total": 0, "successful": 0, "failed": 0}
                    },
                    "sops": {
                        "nsw": {"total": 0, "successful": 0, "failed": 0},
                        "qld": {"total": 0, "successful": 0, "failed": 0},
                        "wa": {"total": 0, "successful": 0, "failed": 0}
                    }
                },
                "last_update": "",
                "total_documents_processed": 0,
                "total_successful": 0,
                "total_failed": 0
            }
    
    def log_document(self, region: str, doc_type: str, url: str, success: bool, metadata: Optional[Dict] = None) -> None:
        """Log a document processing event."""
        timestamp = datetime.now().isoformat()
        
        doc_entry = {
            "timestamp": timestamp,
            "region": region,
            "type": doc_type,
            "url": url,
            "success": success
        }
        
        if metadata:
            doc_entry["metadata"] = metadata
        
        self.current_session["documents"].append(doc_entry)
        self.current_session["stats"]["total_processed"] += 1
        if success:
            self.current_session["stats"]["successful"] += 1
        else:
            self.current_session["stats"]["failed"] += 1
        
        # Update audit log statistics
        self.audit_log["document_stats"][doc_type][region]["total"] += 1
        if success:
            self.audit_log["document_stats"][doc_type][region]["successful"] += 1
        else:
            self.audit_log["document_stats"][doc_type][region]["failed"] += 1
        
        self._save_audit_log()
    
    def log_error(self, region: str, url: str, message: str, error_type: str) -> None:
        """Log an error event."""
        timestamp = datetime.now().isoformat()
        
        error_entry = {
            "timestamp": timestamp,
            "region": region,
            "url": url,
            "error_type": error_type,
            "message": message
        }
        
        self.current_session["errors"].append(error_entry)
        self._save_audit_log()
    
    def get_region_summary(self, region: str) -> Dict:
        """Get summary statistics for a region."""
        summary = {
            "total_downloads": 0,
            "total_errors": 0,
            "successful_downloads": 0,
            "failed_downloads": 0
        }
        
        # Count documents
        for doc in self.current_session["documents"]:
            if doc["region"] == region:
                summary["total_downloads"] += 1
                if doc["success"]:
                    summary["successful_downloads"] += 1
                else:
                    summary["failed_downloads"] += 1
        
        # Count errors
        summary["total_errors"] = len([
            e for e in self.current_session["errors"]
            if e["region"] == region
        ])
        
        return summary
    
    def finalize_session(self) -> None:
        """Finalize the current scraping session and update audit log."""
        self.current_session["end_time"] = datetime.now().isoformat()
        self.audit_log["scraping_history"].append(self.current_session)
        
        # Update global statistics
        self.audit_log["total_documents_processed"] += self.current_session["stats"]["total_processed"]
        self.audit_log["total_successful"] += self.current_session["stats"]["successful"]
        self.audit_log["total_failed"] += self.current_session["stats"]["failed"]
        self.audit_log["last_update"] = datetime.now().isoformat()
        
        self._save_audit_log()
        
        # Reset current session
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "documents": [],
            "errors": [],
            "stats": {
                "total_processed": 0,
                "successful": 0,
                "failed": 0
            }
        }
    
    def _save_audit_log(self) -> None:
        """Save the audit log to file."""
        with open(self.audit_file, "w") as f:
            json.dump(self.audit_log, f, indent=2) 