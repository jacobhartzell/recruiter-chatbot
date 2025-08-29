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
from src.logger import get_logger
import yaml
import time
from datetime import datetime, timedelta

# Initialize GCP logger
logger = get_logger()

def load_config():
    """Load configuration from YAML file."""
    with open('configs/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def check_rate_limit(config):
    """Check if user has exceeded rate limit. Returns True if allowed, False if blocked."""
    # Rate limiting configuration from config
    MAX_REQUESTS_PER_MINUTE = config['rate_limiting']['max_requests_per_minute']
    MAX_REQUESTS_PER_HOUR = config['rate_limiting']['max_requests_per_hour']
    
    # Initialize session state for rate limiting
    if 'request_times' not in st.session_state:
        st.session_state.request_times = []
    
    current_time = datetime.now()
    
    # Clean old requests (older than 1 hour)
    st.session_state.request_times = [
        req_time for req_time in st.session_state.request_times 
        if current_time - req_time < timedelta(hours=1)
    ]
    
    # Check rate limits
    recent_requests = [
        req_time for req_time in st.session_state.request_times 
        if current_time - req_time < timedelta(minutes=1)
    ]
    
    if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
        logger.log_rate_limit_event("exceeded", {
            "limit_type": "per_minute",
            "limit_value": MAX_REQUESTS_PER_MINUTE,
            "current_count": len(recent_requests),
            "session_id": id(st.session_state)
        })
        return False, f"Rate limit exceeded: Maximum {MAX_REQUESTS_PER_MINUTE} requests per minute"
    
    if len(st.session_state.request_times) >= MAX_REQUESTS_PER_HOUR:
        logger.log_rate_limit_event("exceeded", {
            "limit_type": "per_hour", 
            "limit_value": MAX_REQUESTS_PER_HOUR,
            "current_count": len(st.session_state.request_times),
            "session_id": id(st.session_state)
        })
        return False, f"Rate limit exceeded: Maximum {MAX_REQUESTS_PER_HOUR} requests per hour"
    
    # Add current request time
    st.session_state.request_times.append(current_time)
    return True, None

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system."""
    model_name = 'gemini-2.0-flash-001'
    
    try:
        rag_system = RAGSystem(model_name=model_name)
        
        # Show initialization stats
        stats = rag_system.get_stats()
        if "error" not in stats:
            st.success(f"✅ Loaded {stats['documents_loaded']} document chunks")
            
            # Log successful initialization
            logger.log_system_event(
                event_type="rag_system_initialization",
                message="RAG system initialized successfully",
                level="INFO",
                metadata={
                    "model_name": model_name,
                    "documents_loaded": stats.get('documents_loaded', 0),
                    "stats": stats
                }
            )
        
        return rag_system
    except Exception as e:
        logger.log_system_event(
            event_type="rag_system_initialization_error",
            message=f"Failed to initialize RAG system: {str(e)}",
            level="ERROR",
            metadata={"model_name": model_name}
        )
        st.error(f"Failed to initialize chatbot: {e}")
        return None

def main():
    """Main Streamlit application."""
    config = load_config()
    model_name = 'gemini-2.0-flash-001'  # TODO: Move to config

    st.set_page_config(
        page_title=config['streamlit']['page_title'],
        page_icon=config['streamlit']['page_icon'],
        layout=config['streamlit']['layout']
    )


    # Sidebar with personal links
    st.sidebar.title("🔗 Jacob's Links")
    st.sidebar.markdown("""
    Connect with Jacob:
    
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/jacobhartzell)
    
    [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jacobhartzell)
    """, unsafe_allow_html=True)

    st.title("Jacob's Personall Career Assistant")
    st.write("Hi! I'm an AI assisting Jacob in his job search.")
    st.write("Ask me anything about his professional experience and qualifications!")

    # Initialize RAG system
    rag_system = initialize_rag_system()
    if rag_system is None:
        st.stop()  # Stop execution if RAG system failed to initialize

    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="data/resources/robot-me-small.png"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know about my experience?"):
        # Check rate limit before processing
        is_allowed, error_message = check_rate_limit(config)
        
        if not is_allowed:
            st.error(error_message)
            st.info("Please wait a moment before submitting another question.")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant", avatar="data/resources/robot-me-small.png"):
            with st.spinner("Searching my experience and thinking..."):
                try:
                    # Generate response using RAG system
                    response = rag_system.query(prompt)
                    st.markdown(response)
                    
                    # Log chat interaction with structured data
                    logger.log_chat_interaction(
                        user_input=prompt,
                        bot_response=response,
                        metadata={
                            "session_id": id(st.session_state),
                            "response_time": datetime.now().isoformat(),
                            "rag_system_model": model_name
                        }
                    )
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    response = "I apologize, but I'm experiencing technical difficulties. Please try again."
                    st.markdown(response)
                    
                    # Log error event
                    logger.log_system_event(
                        event_type="response_generation_error",
                        message=f"Failed to generate response: {str(e)}",
                        level="ERROR",
                        metadata={
                            "session_id": id(st.session_state),
                            "user_input": prompt
                        }
                    )

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure logs are flushed on exit
        logger.flush()
