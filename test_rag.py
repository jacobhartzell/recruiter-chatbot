#!/usr/bin/env python3
"""
RAG testing script - supports interactive Q&A or batch processing from file.

Usage:
    python test_rag.py                    # Interactive mode
    python test_rag.py questions.txt      # Batch mode with questions file
    python test_rag.py questions.txt -o output.txt  # Batch mode with output file
"""

import os
import shutil
import sys
import argparse
from datetime import datetime
sys.path.append('src')

from rag_system import RAGSystem

def delete_vector_store():
    """Delete the existing vector store for fresh start."""
    vector_db_path = "./chroma_db"
    if os.path.exists(vector_db_path):
        print(f"🗑️  Deleting vector store at {vector_db_path}")
        shutil.rmtree(vector_db_path)
        print("✅ Vector store deleted")
    else:
        print("ℹ️  No existing vector store found")

def get_system_prompt(rag_system):
    """Extract the current system prompt from the RAG system."""
    try:
        # Get the system message without context to see the base prompt
        return rag_system.llm_interface._build_system_message(context=None)
    except Exception as e:
        return f"Error retrieving system prompt: {e}"

def process_batch_questions(questions_file, output_file=None):
    """Process questions from file and output results."""
    
    print("=" * 50)
    print("🤖 RAG System Batch Tester")
    print("=" * 50)
    
    # Delete existing vector store
    delete_vector_store()
    
    # Initialize fresh RAG system
    print("\n🔧 Initializing fresh RAG system...")
    try:
        rag = RAGSystem()
        stats = rag.get_stats()
        print(f"✅ RAG initialized successfully!")
        print(f"   📄 Documents loaded: {stats['documents_loaded']}")
        print(f"   🤖 Model: {stats['model']}")
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        return
    
    # Read questions
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = [line.strip() for line in f.readlines() if line.strip()]
        print(f"📝 Loaded {len(questions)} questions from {questions_file}")
    except Exception as e:
        print(f"❌ Error reading questions file: {e}")
        return
    
    # Get system prompt
    system_prompt = get_system_prompt(rag)
    
    # Prepare output
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_lines = []
    
    # Header with metadata
    output_lines.append("=" * 80)
    output_lines.append(f"RAG SYSTEM TEST RESULTS")
    output_lines.append(f"Timestamp: {timestamp}")
    output_lines.append(f"Questions File: {questions_file}")
    output_lines.append(f"Documents Loaded: {stats['documents_loaded']}")
    output_lines.append(f"Model: {stats['model']}")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # System prompt section
    output_lines.append("SYSTEM PROMPT:")
    output_lines.append("-" * 40)
    output_lines.append(system_prompt)
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Process each question
    print(f"\n🔄 Processing {len(questions)} questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"   {i}/{len(questions)}: {question[:50]}{'...' if len(question) > 50 else ''}")
        
        try:
            response = rag.query(question)
            
            # Format Q&A pair
            output_lines.append(f"QUESTION {i}:")
            output_lines.append(f"Q: {question}")
            output_lines.append("")
            output_lines.append("ANSWER:")
            output_lines.append(f"A: {response}")
            output_lines.append("")
            output_lines.append("-" * 80)
            output_lines.append("")
            
        except Exception as e:
            output_lines.append(f"QUESTION {i}:")
            output_lines.append(f"Q: {question}")
            output_lines.append("")
            output_lines.append("ANSWER:")
            output_lines.append(f"A: ERROR - {e}")
            output_lines.append("")
            output_lines.append("-" * 80)
            output_lines.append("")
    
    # Output results
    output_content = "\n".join(output_lines)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✅ Results saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            print("Printing results to console instead:")
            print("\n" + output_content)
    else:
        # Auto-generate filename
        base_name = os.path.splitext(questions_file)[0]
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{base_name}_results_{timestamp_str}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✅ Results saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            print("Printing results to console instead:")
            print("\n" + output_content)

def interactive_mode():
    """Run interactive Q&A session."""
    print("=" * 50)
    print("🤖 RAG System Interactive Tester")
    print("=" * 50)
    
    # Delete existing vector store
    delete_vector_store()
    
    # Initialize fresh RAG system
    print("\n🔧 Initializing fresh RAG system...")
    try:
        rag = RAGSystem()
        stats = rag.get_stats()
        print(f"✅ RAG initialized successfully!")
        print(f"   📄 Documents loaded: {stats['documents_loaded']}")
        print(f"   🤖 Model: {stats['model']}")
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        return
    
    # Start Q&A session
    print("\n" + "=" * 50)
    print("💬 Ask questions! (type 'quit' to exit)")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n🔍 Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
                
            print("🤔 Thinking...")
            response = rag.query(question)
            print(f"💡 Response: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="RAG System Tester - Interactive or Batch Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'questions_file', 
        nargs='?', 
        help='Text file with questions (one per line) for batch processing'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for batch results (auto-generated if not specified)'
    )
    
    args = parser.parse_args()
    
    if args.questions_file:
        # Batch mode
        if not os.path.exists(args.questions_file):
            print(f"❌ Questions file not found: {args.questions_file}")
            return
        process_batch_questions(args.questions_file, args.output)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()