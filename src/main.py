"""
Main entry point for the Recruiter Chatbot application.

This module provides a simple CLI interface for the RAG system.
For the web interface, use streamlit_app.py instead.
"""

import logging
import sys
from pathlib import Path

from src.utils import fix_sqlite_compatibility

# Apply SQLite compatibility fix
fix_sqlite_compatibility()

from src.rag_system import RAGSystem
from src.logger import get_logger

# Initialize logger
logger = get_logger()

def main():
    """Initialize and run the RAG system."""
    logger.info("Initializing Recruiter Chatbot...")

    try:
        # Initialize RAG system with default settings
        rag_system = RAGSystem()
        
        # Get system stats
        stats = rag_system.get_stats()
        logger.info(f"RAG system initialized successfully: {stats}")
        
        # Simple interactive loop
        print("\n🤖 Recruiter Chatbot CLI")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("Ask about Jacob's experience: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                if not question:
                    continue
                    
                response = rag_system.query(question)
                print(f"\nBot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"Error: {e}\n")
                
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        print(f"Failed to initialize chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
