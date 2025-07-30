"""
Streamlit web application for the recruiter chatbot.
"""

import streamlit as st
from src.main import RAGSystem
import yaml

def load_config():
    """Load configuration from YAML file."""
    with open('configs/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def initialize_rag_system():
    """Initialize the RAG system."""
    # TODO: Initialize RAG system components
    pass

def main():
    """Main Streamlit application."""
    config = load_config()
    
    st.set_page_config(
        page_title=config['streamlit']['page_title'],
        page_icon=config['streamlit']['page_icon'],
        layout=config['streamlit']['layout']
    )
    
    st.title("🤖 Career Chatbot")
    st.write("Ask me anything about my professional experience!")
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state:
        with st.spinner("Initializing chatbot..."):
            st.session_state.rag_system = initialize_rag_system()
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know about my experience?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO: Use RAG system to generate response
                response = "This is a placeholder response. The RAG system will be implemented soon!"
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
