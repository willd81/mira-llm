# MIRA Mining LLM Data Pipeline

A modular data acquisition and processing pipeline for mining-specific documents to train specialized language models.

## System Architecture

The pipeline is organized into five main components:

1. **Scrapers**: Extract content from various sources
2. **Processors**: Clean and structure the extracted content
3. **Transformers**: Chunk and tag content for embedding and retrieval
4. **Embeddings**: Generate vector embeddings and provide search functionality
5. **API**: Expose search and RAG capabilities through FastAPI endpoints

## Directory Structure

```
mira-llm/
├── pipeline/                 # Orchestration scripts
│   ├── run_pipeline.py       # Main entry point
│   ├── scraper_pipeline.py   # Scraper orchestration
│   ├── cleaner_pipeline.py   # Cleaner orchestration
│   └── chunking_pipeline.py  # Chunking orchestration
│
├── scrapers/                 # Content extraction modules
│   ├── sources/              # Source-specific scrapers
│   │   ├── html_scraper.py   # Standard HTML scraper
│   │   ├── pdf_scraper.py    # PDF document scraper
│   │   └── embedded_scraper.py # Embedded text scraper
│   │
│   └── utils/                # Scraper utilities
│       ├── base_scraper.py   # Base scraper class
│       └── scraper_factory.py # Factory for creating scrapers
│
├── processors/               # Content processing modules
│   ├── cleaners/             # Content cleaning modules
│   │   ├── html_cleaner.py   # HTML content cleaner
│   │   ├── pdf_cleaner.py    # PDF content cleaner
│   │   └── embedded_cleaner.py # Embedded text cleaner
│   │
│   ├── transformers/         # Content transformation modules
│   │   ├── chunker.py        # Text chunking for RAG
│   │   └── metadata_tagger.py # Mining-specific metadata tagger
│   │
│   └── utils/                # Processor utilities
│       └── base_cleaner.py   # Base cleaner class
│
├── embeddings/               # Embedding and vector search modules
│   ├── models.py             # Embedding model interfaces
│   ├── vector_stores.py      # Vector database interfaces
│   ├── embedding_pipeline.py # Embedding pipeline
│   ├── search.py             # Search functionality
│   ├── rag.py                # RAG functionality
│   └── config.py             # Configuration utilities
│
├── api/                      # API modules
│   └── server.py             # FastAPI server
│
├── scraper/                  # Legacy scraper code (for reference)
│   ├── config/               # Configuration files
│   │   └── config.yaml       # Source definitions
│   └── ...                   # Other legacy modules
│
└── data/                     # Data storage
    ├── raw/                  # Raw scraped content
    ├── cleaned/              # Cleaned and structured content
    ├── chunks/               # Chunked content for RAG
    ├── tagged_chunks/        # Tagged chunks with metadata
    └── vector_indices/       # Vector embeddings and indices
```

## Flow Diagram

```
                       ┌─────────────────┐
                       │   config.yaml   │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │ ScraperPipeline │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │ ScraperFactory  │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
┌─────────────▼─────┐ ┌─────────▼─────┐ ┌─────────▼─────┐
│   HTMLScraper     │ │   PDFScraper  │ │ EmbeddedScraper│
└─────────┬─────────┘ └──────┬────────┘ └───────┬───────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │    raw data     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ CleanerPipeline │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  cleaned data   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ChunkingPipeline │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  tagged chunks  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │EmbeddingPipeline│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Vector Database │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Search & RAG   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   API Server    │
                    └─────────────────┘
```

## Usage

### Running the Full Pipeline

```bash
python -m pipeline.run_pipeline
```

### Running Specific Pipeline Stages

```bash
# Only scrape sources
python -m pipeline.run_pipeline --scrape-only

# Only clean scraped data
python -m pipeline.run_pipeline --clean-only

# Only chunk and tag cleaned data
python -m pipeline.run_pipeline --chunk-only

# Skip chunking step
python -m pipeline.run_pipeline --skip-chunking

# Skip tagging step
python -m pipeline.run_pipeline --skip-tagging

# Customize chunk size
python -m pipeline.run_pipeline --chunk-size 1500 --chunk-overlap 300
```

### Running the Embedding Pipeline

```bash
python -m embeddings.embedding_pipeline \
  --input_dir data/tagged_chunks \
  --vector_store_path data/vector_indices/mira \
  --embedding_model openai
```

### Testing Search Functionality

```bash
python -m embeddings.search "mining safety regulations" \
  --vector_store_path data/vector_indices/mira \
  --top_k 5 \
  --region australia
```

### Using RAG for Question Answering

```bash
python -m embeddings.rag "What are the main safety procedures for underground mining?" \
  --vector_store_path data/vector_indices/mira \
  --llm_model openai
```

### Starting the API Server

```bash
python -m api.server
```

## Adding New Sources

1. Add the source to `scraper/config/config.yaml`
2. The pipeline will automatically classify the source and use the appropriate scraper
3. For specialized sources, create a new scraper class and add it to the ScraperFactory

## Mining-Specific Metadata Tagging

The system automatically tags chunks with mining-specific metadata:

- **Equipment**: Identifies mentions of mining equipment (e.g., longwall, conveyor, ventilation)
- **Hazards**: Identifies safety hazards (e.g., dust, gas, explosion)
- **Procedures**: Tags content related to procedures (e.g., safety procedure, evacuation)
- **Regulations**: Identifies regulatory content (e.g., compliance, legislation, codes of practice)
- **Mining Methods**: Tags different mining methods (e.g., underground, surface, longwall)
- **Minerals**: Identifies mentions of minerals (e.g., coal, gold, iron)

This metadata enables advanced filtering and search capabilities in RAG applications.

## Vector Search and RAG

The system provides advanced vector search and RAG capabilities:

- **Embedding Models**: OpenAI and HuggingFace embedding models
- **Vector Stores**: FAISS (local) and Pinecone (cloud) vector databases
- **Metadata Filtering**: Filter search results by region, document type, and tags
- **RAG Integration**: Generate responses from LLMs with context from retrieved documents
- **API Endpoints**: Search and RAG functionality exposed through FastAPI endpoints

## Development

### Adding a New Scraper

1. Create a new class that extends `BaseScraper`
2. Implement the `process()` method
3. Add the scraper to `ScraperFactory.create_scraper()`

### Adding a New Cleaner

1. Create a new class that extends `BaseCleaner`
2. Implement the `clean_file()` and `clean()` methods
3. Add the cleaner to `CleanerPipeline.__init__()`

### Adding New Metadata Tags

1. Open `processors/transformers/metadata_tagger.py`
2. Add new keyword dictionaries in the `_init_keyword_dictionaries()` method
3. Update the `_extract_tags()` method to handle the new tag categories

### Adding a New Embedding Model

1. Open `embeddings/models.py`
2. Create a new class that extends `EmbeddingModel`
3. Implement the required methods
4. Update the `get_embedding_model()` factory function

### Adding a New Vector Store

1. Open `embeddings/vector_stores.py`
2. Create a new class that extends `VectorStore`
3. Implement the required methods
4. Update the `get_vector_store()` factory function

## Reports and Analytics

Generate reports about the processed data:

```bash
# Generate a report of cleaned data
python -m scripts.generate_report

# Generate a report of chunked and tagged data
python -m scripts.generate_chunk_report
```

## Environment Setup

1. Copy `env.example` to `.env` and fill in your API keys:

```bash
cp env.example .env
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Docker Deployment

Build and run the API server using Docker:

```bash
docker build -t mira-llm .
docker run -p 8000:8000 -v $(pwd)/data:/app/data --env-file .env mira-llm
```

## API Documentation

Once the API server is running, access the API documentation at:

```
http://localhost:8000/docs
```

## Next Steps

- Implement vector database integration for RAG applications
- Add embedding utilities for chunk vectorization
- Create tools for fine-tuning integration with specialized LLMs

