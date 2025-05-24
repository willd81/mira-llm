#!/usr/bin/env python
"""
Script to generate a summary report of the cleaned data.
"""
import json
import os
from pathlib import Path
import shutil
from datetime import datetime

def count_entries(directory):
    """Count the number of entries in all cleaned.json files in the directory."""
    total_entries = 0
    total_sources = 0
    total_chars = 0
    regions = {}
    
    # Traverse all cleaned.json files
    for filepath in Path(directory).rglob("cleaned.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Get region/subregion from path
            rel_path = filepath.relative_to(directory)
            parts = rel_path.parts
            
            if len(parts) >= 2:
                region = parts[0]
                subregion = parts[1]
                
                # Initialize region if not exists
                if region not in regions:
                    regions[region] = {}
                
                # Initialize subregion if not exists
                if subregion not in regions[region]:
                    regions[region][subregion] = {
                        "files": 0,
                        "entries": 0,
                        "chars": 0
                    }
                
                # Count entries and chars
                entry_count = len(data)
                char_count = sum(len(entry.get("title", "")) + len(entry.get("body", "")) for entry in data)
                
                # Update counts
                regions[region][subregion]["files"] += 1
                regions[region][subregion]["entries"] += entry_count
                regions[region][subregion]["chars"] += char_count
                
                total_entries += entry_count
                total_chars += char_count
                total_sources += 1
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    return {
        "total_sources": total_sources,
        "total_entries": total_entries,
        "total_chars": total_chars,
        "regions": regions
    }

def format_report(stats, output_file=None):
    """Format the stats into a readable report."""
    report = []
    report.append("# MIRA Mining LLM Data Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append("## Summary")
    report.append(f"- Total sources processed: {stats['total_sources']}")
    report.append(f"- Total entries extracted: {stats['total_entries']}")
    report.append(f"- Total characters: {stats['total_chars']:,}")
    report.append(f"- Estimated tokens (chars/4): {stats['total_chars'] // 4:,}")
    report.append("")
    
    report.append("## Data by Region")
    
    for region, subregions in stats["regions"].items():
        region_entries = sum(sr["entries"] for sr in subregions.values())
        region_chars = sum(sr["chars"] for sr in subregions.values())
        
        report.append(f"### {region.title()}")
        report.append(f"- Entries: {region_entries}")
        report.append(f"- Characters: {region_chars:,}")
        report.append("")
        
        for subregion, counts in subregions.items():
            report.append(f"#### {subregion.title()}")
            report.append(f"- Files: {counts['files']}")
            report.append(f"- Entries: {counts['entries']}")
            report.append(f"- Characters: {counts['chars']:,}")
            report.append("")
    
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
    
    return report_text

def main():
    """Generate a report of the cleaned data."""
    print("📊 Generating report of cleaned data...")
    
    cleaned_dir = Path("data/cleaned")
    if not cleaned_dir.exists():
        print(f"❌ Cleaned data directory not found: {cleaned_dir}")
        return
    
    stats = count_entries(cleaned_dir)
    
    output_file = Path("data/report.md")
    report = format_report(stats, output_file)
    
    print(f"✅ Report generated: {output_file}")
    print("\n--- Preview ---\n")
    print("\n".join(report.split("\n")[:15]))
    print("...\n")
    
    # Copy to docs for reference
    shutil.copy(output_file, Path("docs/DATA_REPORT.md"))
    print(f"📋 Report also copied to: docs/DATA_REPORT.md")

if __name__ == "__main__":
    main() 