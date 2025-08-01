"""
Vector store implementation using ChromaDB.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import uuid

class VectorStore:
    """ChromaDB-based vector store for document embeddings."""
    
    def __init__(self, persist_directory: str, collection_name: str):
        """Initialize ChromaDB client and collection."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use default embedding function (simpler, no external dependencies)
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=default_ef,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def add_documents(self, documents: List[str], metadatas: List[Dict]):
        """Add documents and their embeddings to the vector store."""
        # Handle empty lists gracefully
        if not documents:
            return
            
        # Generate unique IDs for each document
        ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # Add documents to collection (ChromaDB will generate embeddings automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict]:
        """Perform similarity search and return top k results."""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Format results into a more usable structure
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results['distances'][0] else 0.0,
                    'id': results['ids'][0][i]
                })
        
        return formatted_results
