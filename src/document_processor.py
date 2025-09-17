"""
Document processing utilities for loading and chunking documents.

This module provides functionality to load markdown documents from a directory
and split them into smaller chunks suitable for vector storage and retrieval.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List


class DocumentProcessor:
    """Handle document loading and processing for the RAG system."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor with chunking parameters.
        
        Args:
            chunk_size: Maximum size of each document chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def load_documents(self, directory_path: str) -> List[Document]:
        """
        Load markdown documents from a directory.
        
        Args:
            directory_path: Path to directory containing markdown files
            
        Returns:
            List of Document objects containing the loaded content
        """
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for vector storage.
        
        Args:
            documents: List of Document objects to chunk
            
        Returns:
            List of Document objects representing the chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        return chunks
