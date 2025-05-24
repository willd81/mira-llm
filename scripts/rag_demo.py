#!/usr/bin/env python
"""
Demo script showing how to use the tagged chunks with a vector database for RAG applications.
This is a simplified demonstration that doesn't require external dependencies.
"""
import json
import os
from pathlib import Path
import re
import random
from typing import List, Dict, Any
import argparse

class SimpleEmbedder:
    """
    A simplified embedder that creates mock vector representations.
    In a real application, you would use a proper embedding model.
    """
    
    def embed_text(self, text: str) -> List[float]:
        """Create a mock embedding vector for demonstration purposes."""
        # This is a simplified mock embedding - not for real use
        # In a real application, you would use a model like OpenAI's text-embedding-ada-002
        hash_val = hash(text.lower()) % 10000
        random.seed(hash_val)
        return [random.uniform(-1, 1) for _ in range(5)]

class SimpleVectorDB:
    """
    A simplified in-memory vector database for demonstration purposes.
    In a real application, you would use a proper vector database like FAISS, Pinecone, etc.
    """
    
    def __init__(self):
        self.vectors = []
        self.documents = []
        self.embedder = SimpleEmbedder()
    
    def add_document(self, doc: Dict[str, Any]):
        """
        Add a document to the vector database.
        
        Args:
            doc: Document with text and metadata
        """
        # Create embedding for the document
        text = f"{doc.get('title', '')} {doc.get('text', '')}"
        vector = self.embedder.embed_text(text)
        
        # Store the vector and document
        self.vectors.append(vector)
        self.documents.append(doc)
    
    def similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = sum(a * a for a in v1) ** 0.5
        mag2 = sum(b * b for b in v2) ** 0.5
        return dot_product / (mag1 * mag2) if mag1 * mag2 > 0 else 0
    
    def search(self, query: str, k: int = 5, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query with optional metadata filtering.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Dictionary of metadata filters
            
        Returns:
            List of matching documents with similarity scores
        """
        # Embed the query
        query_vector = self.embedder.embed_text(query)
        
        # Calculate similarities and filter by metadata if needed
        results = []
        for i, doc_vector in enumerate(self.vectors):
            doc = self.documents[i]
            
            # Apply metadata filtering if specified
            if filter_dict and not self._matches_filter(doc, filter_dict):
                continue
                
            # Calculate similarity
            similarity = self.similarity(query_vector, doc_vector)
            
            # Add to results
            results.append({
                "document": doc,
                "similarity": similarity
            })
        
        # Sort by similarity and take top k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:k]
    
    def _matches_filter(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if document matches the metadata filter."""
        metadata = doc.get("metadata", {})
        
        for key, value in filter_dict.items():
            # Special handling for tags
            if key == "tags" and "tags" in metadata:
                # Check if any of the specified tags are present
                tag_match = False
                for category, values in value.items():
                    if category in metadata["tags"]:
                        # Check if any value is present in the tag category
                        for val in values:
                            if val in metadata["tags"][category]:
                                tag_match = True
                                break
                    if tag_match:
                        break
                if not tag_match:
                    return False
            # Regular metadata matching
            elif key in metadata:
                if metadata[key] != value:
                    return False
            else:
                return False
                
        return True

def load_chunks(directory: str = "data/tagged_chunks") -> List[Dict[str, Any]]:
    """
    Load all tagged chunks from the specified directory.
    
    Args:
        directory: Directory containing tagged chunks
        
    Returns:
        List of chunks with text and metadata
    """
    chunks = []
    
    # Recursively find all tagged chunk files
    for filepath in Path(directory).rglob("*_tagged.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_chunks = json.load(f)
                chunks.extend(file_chunks)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    print(f"Loaded {len(chunks)} chunks from {directory}")
    return chunks

def demo_rag_search():
    """Run a demonstration of RAG search with metadata filtering."""
    # Load chunks
    chunks = load_chunks()
    if not chunks:
        print("⚠️ No chunks found. Please run the chunking pipeline first.")
        return
    
    # Create and populate vector database
    db = SimpleVectorDB()
    for chunk in chunks:
        db.add_document(chunk)
    
    print(f"📚 Vector database created with {len(chunks)} documents.")
    
    # Example queries
    example_queries = [
        {
            "query": "What are the safety procedures for underground mining?",
            "filter": None
        },
        {
            "query": "How to handle dust hazards in mining?",
            "filter": {
                "tags": {
                    "hazard": ["dust"]
                }
            }
        },
        {
            "query": "What regulations apply to mining equipment maintenance?",
            "filter": {
                "tags": {
                    "equipment": ["ventilation", "conveyor"],
                    "procedure": ["maintenance"]
                },
                "document_type": "regulatory"
            }
        }
    ]
    
    # Run example searches
    for i, example in enumerate(example_queries, 1):
        query = example["query"]
        filter_dict = example["filter"]
        
        print(f"\n📝 Example {i}: {query}")
        if filter_dict:
            print(f"🔍 Filter: {json.dumps(filter_dict, indent=2)}")
        
        # Search with or without filter
        results = db.search(query, k=3, filter_dict=filter_dict)
        
        # Display results
        print(f"📊 Results ({len(results)}):")
        for j, result in enumerate(results, 1):
            doc = result["document"]
            print(f"  {j}. [{result['similarity']:.2f}] {doc.get('title', 'Untitled')}")
            print(f"     Source: {doc.get('metadata', {}).get('source', 'Unknown')}")
            print(f"     Tags: {', '.join(': '.join([k, ', '.join(v)]) for k, v in doc.get('metadata', {}).get('tags', {}).items())}")
            text = doc.get("text", "").strip()
            print(f"     Text: {text[:100]}..." if len(text) > 100 else f"     Text: {text}")
            print()

if __name__ == "__main__":
    print("🤖 Mining RAG Demo - Using Tagged Chunks for Retrieval")
    demo_rag_search() 