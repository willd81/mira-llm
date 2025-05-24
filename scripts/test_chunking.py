#!/usr/bin/env python
"""
Test script to verify the chunking and tagging functionality.
"""
import json
import shutil
from pathlib import Path

from processors.transformers.chunker import TextChunker
from processors.transformers.metadata_tagger import MetadataTagger

def create_sample_data():
    """Create sample cleaned data for testing the chunking and tagging."""
    # Create test directory structure
    raw_dir = Path("data/cleaned/test/mining_safety")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a sample cleaned data file with mining-specific content
    sample_data = [
        {
            "title": "Underground Mining Safety Guidelines",
            "body": """
Safety is paramount in all underground mining operations. This document outlines key safety procedures.

# Equipment Inspection
Always inspect equipment before entering the mine. Ensure that all safety mechanisms are operational.
Check ventilation systems and gas monitors for proper functioning. 
Test emergency stop buttons and communication devices.

# Hazard Management
Be aware of potential hazards such as dust, methane gas, and roof fall risks.
Conduct regular gas testing and monitoring for explosive gases.
Follow evacuation procedures in case of any emergency.

# Standard Operating Procedures
All personnel must be familiar with standard operating procedures for longwall mining operations.
Follow the proper protocols for equipment operation and maintenance.
Adhere to all regulations and compliance requirements as per the Mines Safety Act.
            """
        },
        {
            "title": "Surface Mining Equipment Maintenance",
            "body": """
Proper maintenance of mining equipment is essential for safe operations in open pit mining.

# Dragline and Excavator Maintenance
Inspect all mechanical components daily before operation.
Check for hydraulic leaks, worn cables, and structural integrity.
Follow manufacturer's guidelines for preventive maintenance schedules.

# Haul Truck Safety
Perform pre-operation checks of braking systems and steering mechanisms.
Ensure proper functioning of backup alarms and proximity detection systems.
Follow proper loading procedures to prevent spillage or overloading.

# Regulatory Compliance
All maintenance activities must comply with equipment safety standards.
Maintain detailed maintenance logs as required by mining regulations.
Ensure all technicians are properly trained and certified for the specific equipment.
            """
        }
    ]
    
    with open(raw_dir / "cleaned.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Created sample cleaned data at {raw_dir / 'cleaned.json'}")
    return raw_dir

def test_chunking_and_tagging():
    """Test the chunking and tagging functionality on sample data."""
    # Create sample data
    cleaned_dir = create_sample_data()
    
    # Set up test directories
    chunks_dir = Path("data/chunks/test")
    tagged_dir = Path("data/tagged_chunks/test")
    
    # Clean up any existing test data
    for dir_path in [chunks_dir, tagged_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    # Create the chunker and process the sample data
    print("\n🧩 Testing chunking functionality...")
    chunker = TextChunker(
        input_dir="data/cleaned",
        output_dir="data/chunks",
        chunk_size=500,  # Smaller chunks for testing
        chunk_overlap=100
    )
    
    # Process the sample file
    chunks = chunker.process_file(cleaned_dir / "cleaned.json")
    print(f"✅ Created {len(chunks)} chunks from sample data")
    
    # Verify chunks were created
    chunk_file = Path("data/chunks/test/mining_safety/cleaned_chunks.json")
    if not chunk_file.exists():
        print(f"❌ Failed to create chunk file at {chunk_file}")
        return False
    
    # Preview a chunk
    with open(chunk_file, "r") as f:
        chunk_data = json.load(f)
    
    print("\n📄 First chunk preview:")
    print(f"  Title: {chunk_data[0]['title']}")
    print(f"  Text (first 100 chars): {chunk_data[0]['text'][:100]}...")
    print(f"  Metadata: {json.dumps(chunk_data[0]['metadata'], indent=2)}")
    
    # Test metadata tagging
    print("\n🏷️ Testing metadata tagging functionality...")
    tagger = MetadataTagger(
        input_dir="data/chunks",
        output_dir="data/tagged_chunks"
    )
    
    # Process the chunk file
    tagged_chunks = tagger.process_file(chunk_file)
    print(f"✅ Tagged {len(tagged_chunks)} chunks with metadata")
    
    # Verify tagged chunks were created
    tagged_file = Path("data/tagged_chunks/test/mining_safety/cleaned_tagged.json")
    if not tagged_file.exists():
        print(f"❌ Failed to create tagged file at {tagged_file}")
        return False
    
    # Preview a tagged chunk
    with open(tagged_file, "r") as f:
        tagged_data = json.load(f)
    
    print("\n🔖 First tagged chunk preview:")
    print(f"  Title: {tagged_data[0]['title']}")
    print(f"  Tags: {json.dumps(tagged_data[0]['metadata'].get('tags', {}), indent=2)}")
    print(f"  Document Type: {tagged_data[0]['metadata'].get('document_type', 'unknown')}")
    
    return True

def clean_up():
    """Clean up the test data."""
    for dir_path in [
        Path("data/cleaned/test"),
        Path("data/chunks/test"),
        Path("data/tagged_chunks/test")
    ]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    print("🧹 Cleaned up test data")

def main():
    """Main entry point for the test script."""
    print("🔬 Testing Chunking and Tagging Pipeline")
    
    try:
        success = test_chunking_and_tagging()
        
        if success:
            print("\n✅ Chunking and tagging functionality test passed!")
            print("🚀 You can now process your real data with: python -m pipeline.run_pipeline")
        else:
            print("\n❌ Chunking and tagging functionality test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        clean_up()

if __name__ == "__main__":
    main() 