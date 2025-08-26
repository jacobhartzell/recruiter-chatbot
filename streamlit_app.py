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
from src.rag_system import RAGSystem
import yaml
import logging
import time
import os
import threading

# Set up loggingß
logging.basicConfig(filename='/var/log/chatbot.log', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    with open('configs/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def timeout_handler():
    os._exit(0)

# Update on every interaction
st.session_state.last_interaction = time.time()

if "timed_out" not in st.session_state:
    st.session_state.timed_out = False

@st.fragment(run_every=10)
def idle_timeout():
    # Timeout after 30 sec
    if st.session_state.timed_out:
        return
    if time.time() - st.session_state.last_interaction > 30:
        st.session_state.timed_out = True
        st.title("Timeout. Refresh browser to continue.")
        st.rerun()

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system."""
    try:
        rag_system = RAGSystem(model_name='gemini-2.0-flash-001')
        logger.info("RAG system initialized successfully")

        # Show initialization stats
        stats = rag_system.get_stats()
        if "error" not in stats:
            st.success(f"✅ Loaded {stats['documents_loaded']} document chunks")

        return rag_system
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        st.error(f"Failed to initialize chatbot: {e}")
        return None

def main():
    """Main Streamlit application."""
    if st.session_state.get("timed_out"):
        st.warning("Session timed out.")
        logger.info("Exiting due to timeout")
        timer = threading.Timer(10, timeout_handler)
        timer.start()
        st.stop()

    config = load_config()

    st.set_page_config(
        page_title=config['streamlit']['page_title'],
        page_icon=config['streamlit']['page_icon'],
        layout=config['streamlit']['layout']
    )


    st.title("🤖 Career Chatbot")
    st.write("Hi! I'm an AI representing a job candidate. Ask me anything about my professional experience and qualifications!")

    # Initialize RAG system
    rag_system = initialize_rag_system()
    if rag_system is None:
        st.stop()  # Stop execution if RAG system failed to initialize

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
            with st.spinner("Searching my experience and thinking..."):
                try:
                    # Generate response using RAG system
                    response = rag_system.query(prompt)
                    st.markdown(response)
                    logging.info(f'Received Prompt {prompt}')
                    logging.info(f'Responded: {response}')
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    response = "I apologize, but I'm experiencing technical difficulties. Please try again."
                    st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    idle_timeout()
    main()
