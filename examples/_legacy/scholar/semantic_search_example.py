#!/usr/bin/env python3
"""Example: Semantic search for finding related papers."""

import asyncio
from pathlib import Path
from scitex.scholar import Scholar, Paper
from scitex.scholar.database import PaperDatabase
from scitex.scholar.search import SemanticSearchEngine


def semantic_search_example():
    """Demonstrate semantic search capabilities."""

    print("=== SciTeX Scholar - Semantic Search Example ===\n")

    # Initialize components
    db = PaperDatabase()
    engine = SemanticSearchEngine(
        database=db,
        model_name="all-MiniLM-L6-v2",  # Fast and good quality
        index_type="flat",  # Exact search
        use_gpu=False
    )

    # Step 1: Check if we have papers in database
    print("1. Checking database...")
    print("-" * 50)

    if len(db.entries) == 0:
        print("No papers in database. Adding sample papers...")

        # Create sample papers
        sample_papers = [
            Paper(
                title="Deep Learning for Climate Change Prediction",
                abstract="We present a novel deep learning approach for predicting climate patterns...",
                authors=["Jane Smith", "John Doe"],
                year=2024,
                journal="Nature Climate Change",
                doi="10.1038/s41558-024-1234",
                keywords=["deep learning", "climate", "prediction"]
            ),
            Paper(
                title="Transformer Models in Scientific Computing",
                abstract="This paper explores the application of transformer architectures to scientific problems...",
                authors=["Alice Brown"],
                year=2024,
                journal="Science",
                doi="10.1126/science.abc1234",
                keywords=["transformers", "scientific computing", "AI"]
            ),
            Paper(
                title="Machine Learning for Weather Forecasting",
                abstract="A comprehensive review of ML techniques for weather prediction...",
                authors=["Bob Wilson", "Carol Davis"],
                year=2023,
                journal="Weather and Forecasting",
                doi="10.1175/waf-2023-123",
                keywords=["machine learning", "weather", "forecasting"]
            ),
            Paper(
                title="Neural Networks in Climate Modeling",
                abstract="We demonstrate how neural networks can improve climate simulations...",
                authors=["David Lee", "Emma White"],
                year=2023,
                journal="Journal of Climate",
                doi="10.1175/jcli-2023-456",
                keywords=["neural networks", "climate modeling", "simulation"]
            )
        ]

        # Add to database
        db.import_from_papers(sample_papers)
        print(f"Added {len(sample_papers)} sample papers")
    else:
        print(f"Found {len(db.entries)} papers in database")

    # Step 2: Index papers for semantic search
    print("\n2. Indexing papers for semantic search...")
    print("-" * 50)

    stats = engine.index_papers(
        fields=["title", "abstract", "keywords"],
        force_reindex=False  # Skip already indexed
    )

    print(f"Indexed: {stats['indexed']} new papers")
    print(f"Total indexed: {stats['total_indexed']}/{stats['database_size']}")

    # Step 3: Search by text query
    print("\n3. Searching by text query...")
    print("-" * 50)

    query = "deep learning climate prediction"
    print(f"Query: '{query}'")

    results = engine.search_by_text(
        query,
        k=5,
        search_mode="hybrid"  # Combines semantic and keyword search
    )

    print(f"\nFound {len(results)} results:")
    for i, (paper, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.3f}")
        print(f"   Title: {paper.title}")
        print(f"   Year: {paper.year}, Journal: {paper.journal}")
        if paper.abstract:
            print(f"   Abstract: {paper.abstract[:100]}...")

    # Step 4: Find similar papers
    print("\n\n4. Finding similar papers...")
    print("-" * 50)

    if results:
        # Use the top result as reference
        reference_paper = results[0][0]
        print(f"Reference paper: {reference_paper.title}")

        # Find similar papers
        similar = engine.find_similar_papers(
            reference_paper,
            k=3,
            exclude_self=True
        )

        print(f"\nSimilar papers:")
        for i, (paper, similarity) in enumerate(similar, 1):
            print(f"\n{i}. Similarity: {similarity:.3f}")
            print(f"   Title: {paper.title}")
            print(f"   Keywords: {', '.join(paper.keywords) if paper.keywords else 'N/A'}")

    # Step 5: Multi-paper recommendations
    print("\n\n5. Getting recommendations based on multiple papers...")
    print("-" * 50)

    # Get first 2 papers as input
    input_papers = list(db.entries.keys())[:2]
    if len(input_papers) >= 2:
        print(f"Based on {len(input_papers)} papers:")
        for entry_id in input_papers:
            entry = db.get_entry(entry_id)
            print(f"  - {entry.title}")

        recommendations = engine.recommend_papers(
            input_papers,
            k=3,
            method="average"
        )

        print(f"\nRecommended papers:")
        for i, (paper, score) in enumerate(recommendations, 1):
            print(f"\n{i}. Score: {score:.3f}")
            print(f"   Title: {paper.title}")
            print(f"   Year: {paper.year}")

    # Step 6: Search with filters
    print("\n\n6. Searching with metadata filters...")
    print("-" * 50)

    filtered_results = engine.search_similar(
        "machine learning",
        k=10,
        threshold=0.3,
        filters={
            "year_min": 2024,
            "journal": "Nature"  # Partial match
        }
    )

    print(f"Papers about ML from 2024 in Nature journals: {len(filtered_results)}")
    for paper, score in filtered_results:
        print(f"  - {paper.title} ({paper.journal}, {paper.year})")

    # Step 7: Engine statistics
    print("\n\n7. Search Engine Statistics")
    print("-" * 50)

    stats = engine.get_statistics()
    print(f"Embedder model: {stats['embedder']['model_name']}")
    print(f"Embedding dimension: {stats['embedder']['embedding_dim']}")
    print(f"Total indexed: {stats['indexed_entries']}")
    print(f"Coverage: {stats['coverage']:.1%}")
    print(f"Vector DB size: {stats['vector_database']['database_size_mb']:.1f} MB")


def demonstrate_advanced_features():
    """Show advanced semantic search features."""

    print("\n\n=== Advanced Semantic Search Features ===\n")

    db = PaperDatabase()

    # Different embedding models
    print("1. Available embedding models:")
    print("-" * 50)
    print("  - all-MiniLM-L6-v2: Fast, 384 dimensions")
    print("  - all-mpnet-base-v2: High quality, 768 dimensions")
    print("  - allenai-specter: Trained on scientific papers")
    print("  - tfidf: Fallback when sentence-transformers not available")

    # Index types
    print("\n2. Vector index types:")
    print("-" * 50)
    print("  - flat: Exact search (best for <100k papers)")
    print("  - ivf: Approximate search (100k-1M papers)")
    print("  - hnsw: Fast approximate (>1M papers)")

    # Search modes
    print("\n3. Search modes:")
    print("-" * 50)

    engine = SemanticSearchEngine(database=db)

    # Pure semantic
    print("  - semantic: Pure embedding-based search")
    print("    Best for: Finding conceptually similar papers")

    # Pure keyword
    print("  - keyword: Traditional keyword matching")
    print("    Best for: Exact term matches")

    # Hybrid
    print("  - hybrid: Combines semantic and keyword")
    print("    Best for: General search with specific terms")

    # Custom embedding fields
    print("\n4. Custom embedding fields:")
    print("-" * 50)
    print("You can choose which fields to include in embeddings:")
    print("  - Title only: Fast, focuses on main topic")
    print("  - Title + Abstract: Balanced approach")
    print("  - Title + Abstract + Keywords: Most comprehensive")
    print("  - Add Authors: Find papers by research groups")

    # Performance tips
    print("\n5. Performance optimization:")
    print("-" * 50)
    print("  - GPU acceleration: use_gpu=True")
    print("  - Batch indexing: index_papers(batch_size=1000)")
    print("  - Caching: Embeddings cached automatically")
    print("  - Incremental: Only new papers indexed by default")


def check_dependencies():
    """Check and report on optional dependencies."""

    print("\n\n=== Dependency Check ===\n")

    dependencies = {
        "sentence-transformers": "Semantic embeddings",
        "faiss-cpu": "Fast vector search",
        "scikit-learn": "TF-IDF fallback"
    }

    for package, description in dependencies.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}: {description}")
        except ImportError:
            print(f"✗ {package}: {description}")
            print(f"  Install with: pip install {package}")


if __name__ == "__main__":
    # Check dependencies first
    check_dependencies()

    # Run main example
    semantic_search_example()

    # Show advanced features
    demonstrate_advanced_features()

    print("\n\nNote: This example demonstrates:")
    print("1. Indexing papers for semantic search")
    print("2. Text-based search queries")
    print("3. Finding similar papers")
    print("4. Multi-paper recommendations")
    print("5. Filtered search with metadata")
    print("6. Different search modes and options")
