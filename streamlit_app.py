"""
Streamlit web application for the recruiter chatbot.
"""

# SQLite compatibility fix for Streamlit Cloud
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
from src.llm_interface import LLMInterface
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    with open('configs/config.yaml', 'r') as file:
        return yaml.safe_load(file)

@st.cache_resource
def initialize_llm():
    """Initialize the LLM interface."""
    try:
        llm = LLMInterface()
        logger.info("LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        st.error(f"Failed to initialize chatbot: {e}")
        return None

def main():
    """Main Streamlit application."""
    config = load_config()
    
    st.set_page_config(
        page_title=config['streamlit']['page_title'],
        page_icon=config['streamlit']['page_icon'],
        layout=config['streamlit']['layout']
    )
    
    st.title("🤖 Career Chatbot")
    st.write("Hi! I'm an AI representing a job candidate. Ask me anything about my professional experience and qualifications!")
    
    # Initialize LLM
    llm = initialize_llm()
    if llm is None:
        st.stop()  # Stop execution if LLM failed to initialize
    
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
                try:
                    # Generate response using LLM (no context for now)
                    response = llm.generate_response(prompt)
                    st.markdown(response)
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    response = "I apologize, but I'm experiencing technical difficulties. Please try again."
                    st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
