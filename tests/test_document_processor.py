"""
Unit tests for DocumentProcessor class.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
    def test_init(self):
        """Test DocumentProcessor initialization."""
        assert self.processor.chunk_size == 100
        assert self.processor.chunk_overlap == 20
        assert self.processor.text_splitter is not None
        
    def test_init_default_params(self):
        """Test DocumentProcessor initialization with default parameters."""
        default_processor = DocumentProcessor()
        assert default_processor.chunk_size == 1000
        assert default_processor.chunk_overlap == 200
        
    @pytest.fixture
    def temp_markdown_files(self):
        """Create temporary markdown files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            sub_dir = os.path.join(temp_dir, 'subdirectory')
            os.makedirs(sub_dir)
            
            # Create test markdown files
            file1_content = "# Test Document 1\n\nThis is a test document with some content for testing."
            file2_content = "# Test Document 2\n\nThis is another test document with different content."
            
            file1_path = os.path.join(temp_dir, 'test1.md')
            file2_path = os.path.join(sub_dir, 'test2.md')
            
            with open(file1_path, 'w') as f:
                f.write(file1_content)
            with open(file2_path, 'w') as f:
                f.write(file2_content)
                
            yield temp_dir, [file1_path, file2_path]
    
    def test_load_documents(self, temp_markdown_files):
        """Test document loading functionality."""
        temp_dir, file_paths = temp_markdown_files
        
        documents = self.processor.load_documents(temp_dir)
        
        # Should load 2 markdown files
        assert len(documents) == 2
        
        # Check document content
        contents = [doc.page_content for doc in documents]
        assert any("Test Document 1" in content for content in contents)
        assert any("Test Document 2" in content for content in contents)
        
        # Check metadata
        sources = [doc.metadata.get('source', '') for doc in documents]
        assert len(sources) == 2
        assert all(source.endswith('.md') for source in sources)
        
    def test_load_documents_empty_directory(self):
        """Test loading documents from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = self.processor.load_documents(temp_dir)
            assert len(documents) == 0
            
    def test_load_documents_no_markdown_files(self):
        """Test loading documents from directory with no markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-markdown file
            txt_file = os.path.join(temp_dir, 'test.txt')
            with open(txt_file, 'w') as f:
                f.write("This is a text file, not markdown.")
                
            documents = self.processor.load_documents(temp_dir)
            assert len(documents) == 0
            
    def test_chunk_documents(self, temp_markdown_files):
        """Test document chunking functionality."""
        temp_dir, _ = temp_markdown_files
        
        # Load documents first
        documents = self.processor.load_documents(temp_dir)
        assert len(documents) > 0
        
        # Chunk the documents
        chunks = self.processor.chunk_documents(documents)
        
        # Should have at least as many chunks as documents
        assert len(chunks) >= len(documents)
        
        # Check that chunks have content
        for chunk in chunks:
            assert len(chunk.page_content) > 0
            assert hasattr(chunk, 'metadata')
            
        # Check chunk sizes are within expected range
        for chunk in chunks:
            # Should be <= chunk_size (100) plus some buffer for word boundaries
            assert len(chunk.page_content) <= 150  # Some buffer for word boundaries
            
    def test_chunk_documents_empty_list(self):
        """Test chunking empty document list."""
        chunks = self.processor.chunk_documents([])
        assert len(chunks) == 0
        
    def test_chunk_documents_preserves_metadata(self, temp_markdown_files):
        """Test that chunking preserves document metadata."""
        temp_dir, _ = temp_markdown_files
        
        documents = self.processor.load_documents(temp_dir)
        chunks = self.processor.chunk_documents(documents)
        
        # Check that metadata is preserved in chunks
        for chunk in chunks:
            assert 'source' in chunk.metadata
            assert chunk.metadata['source'].endswith('.md')
            
    def test_integration_load_and_chunk(self, temp_markdown_files):
        """Test integration of loading and chunking documents."""
        temp_dir, _ = temp_markdown_files
        
        # Load and chunk in sequence
        documents = self.processor.load_documents(temp_dir)
        chunks = self.processor.chunk_documents(documents)
        
        # Basic checks
        assert len(documents) == 2
        assert len(chunks) >= 2
        
        # Check that original content is preserved across chunks
        original_content = ' '.join(doc.page_content for doc in documents)
        chunk_content = ' '.join(chunk.page_content for chunk in chunks)
        
        # Most words should be preserved (some formatting might change)
        original_words = set(original_content.split())
        chunk_words = set(chunk_content.split())
        
        # At least 80% of words should be preserved
        preserved_ratio = len(original_words.intersection(chunk_words)) / len(original_words)
        assert preserved_ratio >= 0.8


if __name__ == "__main__":
    pytest.main([__file__])