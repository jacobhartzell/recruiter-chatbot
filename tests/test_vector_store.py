"""
Unit tests for VectorStore class.
"""

import pytest
import tempfile
import os
import sys
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vector_store import VectorStore


class TestVectorStore:
    """Test cases for VectorStore class."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
    @pytest.fixture
    def vector_store(self, temp_db_path):
        """Create a VectorStore instance for testing."""
        return VectorStore(
            persist_directory=temp_db_path,
            collection_name="test_collection"
        )
        
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing."""
        return [
            "This is a document about Python programming and data science.",
            "Machine learning is a subset of artificial intelligence.",
            "ChromaDB is a vector database for storing embeddings.",
            "Natural language processing involves analyzing human language."
        ]
        
    @pytest.fixture
    def sample_metadatas(self):
        """Sample metadata for testing."""
        return [
            {"source": "python_doc.md", "topic": "programming"},
            {"source": "ml_doc.md", "topic": "machine_learning"},
            {"source": "chroma_doc.md", "topic": "database"},
            {"source": "nlp_doc.md", "topic": "nlp"}
        ]
    
    def test_init(self, temp_db_path):
        """Test VectorStore initialization."""
        vector_store = VectorStore(temp_db_path, "test_collection")
        
        assert vector_store.persist_directory == temp_db_path
        assert vector_store.collection_name == "test_collection"
        assert vector_store.client is not None
        assert vector_store.collection is not None
        
    def test_init_creates_directory(self):
        """Test that VectorStore creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "new_db")
            assert not os.path.exists(db_path)
            
            vector_store = VectorStore(db_path, "test_collection")
            assert os.path.exists(db_path)
            
    def test_add_documents(self, vector_store, sample_documents, sample_metadatas):
        """Test adding documents to vector store."""
        # Should not raise any exceptions
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        # Verify documents were added by checking collection count
        collection_count = vector_store.collection.count()
        assert collection_count == len(sample_documents)
        
    def test_add_documents_empty_lists(self, vector_store):
        """Test adding empty document and metadata lists."""
        vector_store.add_documents([], [])
        collection_count = vector_store.collection.count()
        assert collection_count == 0
        
    def test_add_documents_mismatched_lengths(self, vector_store):
        """Test adding documents with mismatched document and metadata lengths."""
        documents = ["Document 1", "Document 2"]
        metadatas = [{"source": "doc1.md"}]  # Only one metadata for two documents
        
        # This should handle gracefully or raise appropriate error
        with pytest.raises((ValueError, IndexError)):
            vector_store.add_documents(documents, metadatas)
            
    def test_similarity_search_basic(self, vector_store, sample_documents, sample_metadatas):
        """Test basic similarity search functionality."""
        # Add documents first
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        # Search for programming-related content
        results = vector_store.similarity_search("Python programming", k=2)
        
        assert len(results) <= 2  # Should return at most k results
        assert len(results) > 0   # Should return at least one result
        
        # Check result structure
        for result in results:
            assert 'document' in result
            assert 'metadata' in result
            assert 'distance' in result
            assert 'id' in result
            assert isinstance(result['distance'], (int, float))
            
    def test_similarity_search_empty_collection(self, vector_store):
        """Test similarity search on empty collection."""
        results = vector_store.similarity_search("test query", k=3)
        assert len(results) == 0
        
    def test_similarity_search_k_parameter(self, vector_store, sample_documents, sample_metadatas):
        """Test that k parameter limits results correctly."""
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        # Test different k values
        for k in [1, 2, 3, 10]:
            results = vector_store.similarity_search("programming", k=k)
            expected_results = min(k, len(sample_documents))
            assert len(results) == expected_results
            
    def test_similarity_search_relevance(self, vector_store, sample_documents, sample_metadatas):
        """Test that similarity search returns relevant results."""
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        # Search for "Python" - should return the Python programming document
        results = vector_store.similarity_search("Python", k=1)
        assert len(results) == 1
        
        # The most similar document should contain "Python"
        assert "Python" in results[0]['document']
        
    def test_similarity_search_distances_ordered(self, vector_store, sample_documents, sample_metadatas):
        """Test that similarity search results are ordered by distance."""
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        results = vector_store.similarity_search("machine learning AI", k=3)
        
        if len(results) > 1:
            # Distances should be in ascending order (smaller = more similar)
            for i in range(len(results) - 1):
                assert results[i]['distance'] <= results[i + 1]['distance']
                
    def test_metadata_preservation(self, vector_store, sample_documents, sample_metadatas):
        """Test that metadata is preserved in search results."""
        vector_store.add_documents(sample_documents, sample_metadatas)
        
        results = vector_store.similarity_search("Python", k=1)
        assert len(results) == 1
        
        result_metadata = results[0]['metadata']
        assert 'source' in result_metadata
        assert 'topic' in result_metadata
        assert result_metadata['source'].endswith('.md')
        
    def test_persistence(self, temp_db_path, sample_documents, sample_metadatas):
        """Test that data persists between VectorStore instances."""
        # Create first instance and add documents
        vector_store1 = VectorStore(temp_db_path, "test_collection")
        vector_store1.add_documents(sample_documents, sample_metadatas)
        
        # Create second instance with same path
        vector_store2 = VectorStore(temp_db_path, "test_collection")
        
        # Should be able to search documents added by first instance
        results = vector_store2.similarity_search("Python", k=1)
        assert len(results) == 1
        assert "Python" in results[0]['document']
        
    def test_different_collections(self, temp_db_path, sample_documents, sample_metadatas):
        """Test that different collections are isolated."""
        # Create two collections
        vector_store1 = VectorStore(temp_db_path, "collection1")
        vector_store2 = VectorStore(temp_db_path, "collection2")
        
        # Add documents to first collection only
        vector_store1.add_documents(sample_documents, sample_metadatas)
        
        # Second collection should be empty
        results1 = vector_store1.similarity_search("Python", k=1)
        results2 = vector_store2.similarity_search("Python", k=1)
        
        assert len(results1) == 1
        assert len(results2) == 0
        
    def test_integration_with_real_documents(self, vector_store):
        """Test integration with realistic document data."""
        documents = [
            "# Getting Started with Python\n\nPython is a powerful programming language.",
            "# Machine Learning Basics\n\nMachine learning algorithms learn from data.",
            "# Data Science Tools\n\nPandas and NumPy are essential for data analysis."
        ]
        
        metadatas = [
            {"source": "python_guide.md", "section": "introduction"},
            {"source": "ml_guide.md", "section": "basics"},
            {"source": "data_tools.md", "section": "tools"}
        ]
        
        # Add documents
        vector_store.add_documents(documents, metadatas)
        
        # Test search
        results = vector_store.similarity_search("data analysis tools", k=2)
        
        assert len(results) > 0
        # Should find the data science tools document
        assert any("Pandas" in result['document'] or "NumPy" in result['document'] 
                  for result in results)


if __name__ == "__main__":
    pytest.main([__file__])