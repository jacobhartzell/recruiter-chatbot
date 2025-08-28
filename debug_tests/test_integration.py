#!/usr/bin/env python3
"""
Integration test for rate limiting and logging functionality.
Run this script to test the features locally.
"""

import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.logger import get_logger
from streamlit_app import check_rate_limit, load_config

def test_logging():
    """Test logging functionality."""
    print("Testing logging functionality...")
    
    # Initialize logger
    logger = get_logger()
    
    # Test basic logging
    logger.info("Integration test started")
    logger.debug("This is a debug message")
    logger.warning("This is a warning")
    
    # Test chat interaction logging
    logger.log_chat_interaction(
        user_input="What is your experience with Python?",
        bot_response="I have 5 years of experience with Python development.",
        metadata={
            "session_id": "test_session_123",
            "model_name": "gemini-2.0-flash-001",
            "test_run": True
        }
    )
    
    # Test rate limit logging
    logger.log_rate_limit_event("warning", {
        "limit_type": "per_minute",
        "current_count": 8,
        "limit_value": 10,
        "session_id": "test_session_123"
    })
    
    # Test system event logging
    logger.log_system_event(
        event_type="integration_test",
        message="Integration test completed successfully",
        level="INFO",
        metadata={"test_timestamp": datetime.now().isoformat()}
    )
    
    print("✅ Logging tests completed")

def test_rate_limiting():
    """Test rate limiting functionality."""
    print("Testing rate limiting functionality...")
    
    # Load config
    config = load_config()
    
    # Mock session state
    class MockSessionState:
        def __init__(self):
            self.request_times = []
        
        def __contains__(self, key):
            return hasattr(self, key)
        
        def __getitem__(self, key):
            return getattr(self, key)
        
        def __setitem__(self, key, value):
            setattr(self, key, value)
    
    # Test normal operation
    import streamlit as st
    st.session_state = MockSessionState()
    
    # First request should be allowed
    allowed, message = check_rate_limit(config)
    assert allowed is True
    assert message is None
    print("✅ First request allowed")
    
    # Add multiple recent requests to test per-minute limit
    current_time = datetime.now()
    st.session_state.request_times = [current_time] * config['rate_limiting']['max_requests_per_minute']
    
    # This should be blocked
    allowed, message = check_rate_limit(config)
    assert allowed is False
    assert "per minute" in message
    print("✅ Rate limiting working correctly")
    
    print("✅ Rate limiting tests completed")

def test_log_file_creation():
    """Test that log files are created correctly."""
    print("Testing log file creation...")
    
    # Check if logs directory exists or can be created
    log_dir = "logs"
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"✅ Created log directory: {log_dir}")
        except OSError as e:
            print(f"⚠️ Cannot create log directory: {e}")
            print("Logs will go to console only")
    
    # Test logging to file
    logger = get_logger()
    logger.info("Testing log file creation")
    
    log_file = "logs/chatbot.log"
    if os.path.exists(log_file):
        print(f"✅ Log file created: {log_file}")
        # Show last few lines of log file
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print("Last 3 log entries:")
            for line in lines[-3:]:
                print(f"  {line.strip()}")
    else:
        print("⚠️ Log file not found (console logging only)")

def test_gcp_credentials():
    """Test GCP credentials configuration."""
    print("Testing GCP credentials configuration...")
    
    gcp_json_env = os.getenv('GCP_SERVICE_ACCOUNT_JSON')
    gcp_file_env = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if gcp_json_env:
        print("✅ Found GCP_SERVICE_ACCOUNT_JSON environment variable")
        try:
            import json
            creds = json.loads(gcp_json_env)
            print(f"   Project ID: {creds.get('project_id', 'Not found')}")
            print(f"   Client Email: {creds.get('client_email', 'Not found')}")
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON in GCP_SERVICE_ACCOUNT_JSON")
    elif gcp_file_env:
        print(f"✅ Found GOOGLE_APPLICATION_CREDENTIALS: {gcp_file_env}")
        if os.path.exists(gcp_file_env):
            print("   Credentials file exists")
        else:
            print("   ⚠️ Credentials file not found")
    else:
        print("ℹ️ No GCP credentials configured (using local logging)")
    
    # Test logger initialization with current credentials
    logger = get_logger()
    if logger.config['logging'].get('use_gcp_logging', False):
        if logger.cloud_client:
            print("✅ GCP Cloud Logging client initialized successfully")
        else:
            print("⚠️ GCP logging enabled but client not initialized")
    else:
        print("ℹ️ GCP logging disabled in config")

def main():
    """Run integration tests."""
    print("🚀 Starting integration tests for rate limiting and logging")
    print("=" * 60)
    
    try:
        test_gcp_credentials()
        print()
        
        test_logging()
        print()
        
        test_rate_limiting() 
        print()
        
        test_log_file_creation()
        print()
        
        print("=" * 60)
        print("✅ All integration tests completed successfully!")
        print()
        print("Configuration used:")
        print(f"  - Config file: configs/config.yaml")
        print(f"  - GCP logging: {'Enabled' if get_logger().config['logging'].get('use_gcp_logging') else 'Disabled'}")
        print(f"  - Log level: {get_logger().config['logging']['log_level']}")
        print(f"  - Environment: {get_logger().config['logging']['environment']}")
        print()
        print("To test GCP logging:")
        print("  1. Set up GCP credentials (see GCP_SETUP.md)")
        print("  2. Set environment variable:")
        print("     export GCP_SERVICE_ACCOUNT_JSON='{...json content...}'")
        print("  3. Enable in config: use_gcp_logging: true")
        print("  4. Run this test again")
        
        # Flush logs before exit
        logger = get_logger()
        logger.flush()
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Flush logs even on error
        try:
            logger = get_logger()
            logger.flush()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()