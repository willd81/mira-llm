#!/usr/bin/env python3
"""
Document Counter Script for MIRA-LLM

Counts and categorizes documents in the data directory.
"""
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, DefaultDict
import json

def count_documents(data_dir: str = "./data") -> Dict:
    """
    Count documents in the data directory, grouping by region and file type.
    """
    total_files = 0
    region_counts: DefaultDict[str, int] = defaultdict(int)
    filetype_counts: DefaultDict[str, int] = defaultdict(int)
    region_filetypes: DefaultDict[str, DefaultDict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    # Walk through all directories
    for root, _, files in os.walk(data_dir):
        if "__pycache__" in root or ".git" in root:
            continue
            
        relative_path = os.path.relpath(root, data_dir)
        region = relative_path.split(os.sep)[0] if relative_path != "." else "root"
        
        for file in files:
            if file.startswith('.'):  # Skip hidden files
                continue
                
            total_files += 1
            region_counts[region] += 1
            
            # Get file extension
            ext = os.path.splitext(file)[1].lower() or "no_extension"
            filetype_counts[ext] += 1
            region_filetypes[region][ext] += 1
    
    return {
        "total_files": total_files,
        "by_region": dict(region_counts),
        "by_filetype": dict(filetype_counts),
        "region_filetypes": {k: dict(v) for k, v in region_filetypes.items()}
    }

def format_counts(counts: Dict) -> str:
    """Format count results for display"""
    output = []
    
    # Total files
    output.append(f"\nTotal Files: {counts['total_files']}\n")
    
    # Files by region
    output.append("\nFiles by Region:")
    for region, count in sorted(counts['by_region'].items()):
        output.append(f"  {region}: {count}")
    
    # Files by type
    output.append("\nFiles by Type:")
    for ext, count in sorted(counts['by_filetype'].items()):
        output.append(f"  {ext}: {count}")
    
    # Detailed breakdown by region and type
    output.append("\nDetailed Breakdown by Region and Type:")
    for region, filetypes in sorted(counts['region_filetypes'].items()):
        output.append(f"\n  {region}:")
        for ext, count in sorted(filetypes.items()):
            output.append(f"    {ext}: {count}")
    
    return "\n".join(output)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Count documents in the data directory")
    parser.add_argument("--data-dir", default="./data",
                       help="Path to data directory (default: ./data)")
    parser.add_argument("--json", action="store_true",
                       help="Output in JSON format")
    parser.add_argument("--output", type=str,
                       help="Save output to file")
    
    args = parser.parse_args()
    
    # Count documents
    counts = count_documents(args.data_dir)
    
    # Format output
    if args.json:
        output = json.dumps(counts, indent=2)
    else:
        output = format_counts(counts)
    
    # Save or print
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main() 