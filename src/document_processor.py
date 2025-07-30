"""
Document processing utilities for loading and chunking documents.
"""

from langchain.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

class DocumentProcessor:
    """Handle document loading and processing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize document processor with chunking parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def load_documents(self, directory_path: str) -> List:
        """Load documents from directory."""
        # TODO: Implement document loading using LangChain loaders
        pass
    
    def chunk_documents(self, documents: List) -> List:
        """Split documents into smaller chunks."""
        # TODO: Implement document chunking
        pass
