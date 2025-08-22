"""
Document processing utilities for loading and chunking documents.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
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
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents

    def chunk_documents(self, documents: List) -> List:
        """Split documents into smaller chunks."""
        chunks = self.text_splitter.split_documents(documents)
        return chunks
