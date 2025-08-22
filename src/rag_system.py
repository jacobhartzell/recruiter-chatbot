"""
RAG (Retrieval-Augmented Generation) system for the recruiter chatbot.
"""

import logging
from typing import List, Dict, Any

try:
    # Try relative imports first (for package usage)
    from .document_processor import DocumentProcessor
    from .vector_store import VectorStore
    from .llm_interface import LLMInterface
except ImportError:
    # Fall back to absolute imports (for direct testing)
    from document_processor import DocumentProcessor
    from vector_store import VectorStore
    from llm_interface import LLMInterface

logger = logging.getLogger(__name__)

class RAGSystem:
    """Main RAG system that connects document processing, vector search, and LLM generation."""
    
    def __init__(self, documents_path: str = "data/documents", 
                 vector_db_path: str = "./chroma_db",
                 collection_name: str = "career_docs",
                 **kwargs):
        """Initialize RAG system with all components."""
        logger.info("Initializing RAG system...")
        
        # Initialize components
        self.document_processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        self.vector_store = VectorStore(vector_db_path, collection_name)
        llm_args = {k: v for k, v in kwargs.items() if k in ['model_name', 'max_tokens', 'temperature']}
        self.llm_interface = LLMInterface(**llm_args)
        
        # Load and process documents
        self.documents_path = documents_path
        self._initialize_documents()
        
        logger.info("RAG system initialized successfully")
    
    def _initialize_documents(self):
        """Load documents and add them to vector store if not already present."""
        try:
            # Check if we already have documents in the vector store
            existing_count = self.vector_store.collection.count()
            
            if existing_count == 0:
                logger.info(f"Loading documents from {self.documents_path}")
                
                # Load and process documents
                documents = self.document_processor.load_documents(self.documents_path)
                
                if documents:
                    chunks = self.document_processor.chunk_documents(documents)
                    
                    # Extract text and metadata for vector store
                    chunk_texts = [chunk.page_content for chunk in chunks]
                    chunk_metadatas = [chunk.metadata for chunk in chunks]
                    
                    # Add to vector store
                    self.vector_store.add_documents(chunk_texts, chunk_metadatas)
                    
                    logger.info(f"Added {len(chunk_texts)} document chunks to vector store")
                else:
                    logger.warning(f"No documents found in {self.documents_path}")
            else:
                logger.info(f"Vector store already contains {existing_count} documents")
                
        except Exception as e:
            logger.error(f"Error initializing documents: {e}")
            # Continue without documents - system will still work for basic responses
    
    def query(self, question: str, max_context_chunks: int = 3) -> str:
        """Process a query through the RAG pipeline."""
        try:
            logger.info(f"Processing query: {question}")
            
            # Step 1: Retrieve relevant document chunks
            relevant_chunks = self.vector_store.similarity_search(
                query=question, 
                k=max_context_chunks
            )
            
            # Step 2: Format context from retrieved chunks
            context = self._format_context(relevant_chunks)
            
            # Step 3: Generate response using LLM with context
            response = self.llm_interface.generate_response(
                prompt=question,
                context=context
            )
            
            logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback to LLM without context
            try:
                return self.llm_interface.generate_response(question)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    def _format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into context for the LLM."""
        if not chunks:
            return None
            
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Get source file name for context
            source = chunk.get('metadata', {}).get('source', 'Unknown source')
            source_name = source.split('/')[-1] if '/' in source else source
            
            # Format chunk with source info
            context_parts.append(f"Experience {i} (from {source_name}):\n{chunk['document']}")
        
        formatted_context = "\n\n".join(context_parts)
        logger.info(f"Formatted context from {len(chunks)} chunks")
        
        return formatted_context
    
    def add_documents(self, documents_path: str = None):
        """Add new documents to the vector store."""
        if documents_path is None:
            documents_path = self.documents_path
            
        try:
            logger.info(f"Adding new documents from {documents_path}")
            
            documents = self.document_processor.load_documents(documents_path)
            if documents:
                chunks = self.document_processor.chunk_documents(documents)
                
                chunk_texts = [chunk.page_content for chunk in chunks]
                chunk_metadatas = [chunk.metadata for chunk in chunks]
                
                self.vector_store.add_documents(chunk_texts, chunk_metadatas)
                
                logger.info(f"Added {len(chunk_texts)} new document chunks")
                return len(chunk_texts)
            else:
                logger.warning(f"No documents found in {documents_path}")
                return 0
                
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return 0
    
    def reset_vector_store(self):
        """Reset the vector store by clearing all documents."""
        try:
            logger.info("Resetting vector store...")
            # Delete the collection
            self.vector_store.client.delete_collection(self.vector_store.collection_name)
            
            # Recreate the collection
            self.vector_store.collection = self.vector_store.client.get_or_create_collection(
                name=self.vector_store.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Reload documents
            self._initialize_documents()
            
            logger.info("Vector store reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting vector store: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            doc_count = self.vector_store.collection.count()
            return {
                "documents_loaded": doc_count,
                "vector_store_path": self.vector_store.persist_directory,
                "collection_name": self.vector_store.collection_name,
                "model": self.llm_interface.model_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
