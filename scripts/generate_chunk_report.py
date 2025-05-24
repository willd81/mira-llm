#!/usr/bin/env python
"""
Script to generate a summary report of the chunked and tagged data.
"""
import json
import os
from pathlib import Path
import shutil
from datetime import datetime
from collections import Counter

def count_chunks_and_tags(directory):
    """Count the number of chunks and extract tag statistics."""
    total_chunks = 0
    total_files = 0
    regions = {}
    tag_stats = {
        "document_types": Counter(),
        "equipment": Counter(),
        "hazard": Counter(),
        "procedure": Counter(),
        "regulation": Counter(),
        "mining_method": Counter(),
        "mineral": Counter()
    }
    
    # Traverse all tagged chunk files
    for filepath in Path(directory).rglob("*_tagged.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                
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
                        "chunks": 0,
                        "tagged_chunks": 0
                    }
                
                # Count chunks and tag stats
                chunk_count = len(chunks)
                tagged_count = 0
                
                for chunk in chunks:
                    metadata = chunk.get("metadata", {})
                    doc_type = metadata.get("document_type", "unknown")
                    tag_stats["document_types"][doc_type] += 1
                    
                    tags = metadata.get("tags", {})
                    for category, values in tags.items():
                        if category in tag_stats:
                            for value in values:
                                tag_stats[category][value] += 1
                    
                    if "tags" in metadata:
                        tagged_count += 1
                
                # Update counts
                regions[region][subregion]["files"] += 1
                regions[region][subregion]["chunks"] += chunk_count
                regions[region][subregion]["tagged_chunks"] += tagged_count
                
                total_chunks += chunk_count
                total_files += 1
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    return {
        "total_files": total_files,
        "total_chunks": total_chunks,
        "regions": regions,
        "tag_stats": tag_stats
    }

def format_report(stats, output_file=None):
    """Format the stats into a readable report."""
    report = []
    report.append("# MIRA Mining LLM Chunking Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append("## Summary")
    report.append(f"- Total files processed: {stats['total_files']}")
    report.append(f"- Total chunks generated: {stats['total_chunks']}")
    report.append("")
    
    report.append("## Data by Region")
    
    for region, subregions in stats["regions"].items():
        region_chunks = sum(sr["chunks"] for sr in subregions.values())
        region_tagged = sum(sr["tagged_chunks"] for sr in subregions.values())
        
        report.append(f"### {region.title()}")
        report.append(f"- Total chunks: {region_chunks}")
        report.append(f"- Tagged chunks: {region_tagged}")
        report.append("")
        
        for subregion, counts in subregions.items():
            report.append(f"#### {subregion.title()}")
            report.append(f"- Files: {counts['files']}")
            report.append(f"- Chunks: {counts['chunks']}")
            report.append(f"- Tagged chunks: {counts['tagged_chunks']}")
            report.append("")
    
    report.append("## Document Types")
    for doc_type, count in stats["tag_stats"]["document_types"].most_common():
        report.append(f"- {doc_type}: {count}")
    report.append("")
    
    report.append("## Top Tags by Category")
    
    for category in ["equipment", "hazard", "procedure", "regulation", "mining_method", "mineral"]:
        if stats["tag_stats"][category]:
            report.append(f"### {category.title()}")
            for tag, count in stats["tag_stats"][category].most_common(10):  # Top 10
                report.append(f"- {tag}: {count}")
            report.append("")
    
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
    
    return report_text

def main():
    """Generate a report of the chunked and tagged data."""
    print("📊 Generating report of tagged chunks...")
    
    tagged_dir = Path("data/tagged_chunks")
    if not tagged_dir.exists():
        print(f"❌ Tagged chunks directory not found: {tagged_dir}")
        return
    
    stats = count_chunks_and_tags(tagged_dir)
    
    output_file = Path("data/chunk_report.md")
    report = format_report(stats, output_file)
    
    print(f"✅ Report generated: {output_file}")
    print("\n--- Preview ---\n")
    print("\n".join(report.split("\n")[:15]))
    print("...\n")
    
    # Copy to docs for reference
    shutil.copy(output_file, Path("docs/CHUNK_REPORT.md"))
    print(f"📋 Report also copied to: docs/CHUNK_REPORT.md")

if __name__ == "__main__":
    main() 