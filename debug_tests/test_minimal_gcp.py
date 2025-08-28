#!/usr/bin/env python3
"""
Minimal GCP logging test - bypass our custom logger entirely.
"""

import logging
import os

def test_direct_gcp_logging():
    """Test GCP logging directly without our wrapper."""
    print("Testing direct GCP logging...")
    
    try:
        from google.cloud import logging as cloud_logging
        from google.cloud.logging.handlers import StructuredLogHandler
        
        # Create client
        client = cloud_logging.Client()
        print(f"✅ Client created for project: {client.project}")
        
        # Create handler
        handler = StructuredLogHandler(client=client)
        handler.setLevel(logging.INFO)
        
        # Create simple logger
        logger = logging.getLogger('minimal-test')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()  # Remove any existing handlers
        logger.addHandler(handler)
        
        print("Sending test messages...")
        
        # Send different types of messages
        logger.info("Test message 1: Basic info")
        logger.warning("Test message 2: Warning")
        logger.error("Test message 3: Error")
        
        # Send structured message
        import json
        structured_msg = json.dumps({
            "event_type": "test",
            "service": "minimal-test",
            "message": "Structured test message"
        })
        logger.info(structured_msg)
        
        # Force flush
        handler.flush()
        print("✅ Messages sent and flushed")
        
        # Clean up
        handler.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Direct GCP logging failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cloud_logging_setup():
    """Test the old setup_logging() method."""
    print("\nTesting setup_logging() method...")
    
    try:
        from google.cloud import logging as cloud_logging
        
        client = cloud_logging.Client()
        print(f"✅ Client created: {client.project}")
        
        # This creates the default CloudLoggingHandler
        client.setup_logging()
        print("✅ setup_logging() called")
        
        # Get root logger
        root_logger = logging.getLogger()
        
        print("Sending message via setup_logging()...")
        root_logger.info("Test message via setup_logging()")
        
        print("✅ Message sent via setup_logging()")
        
        return True
        
    except Exception as e:
        print(f"❌ setup_logging() failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run minimal tests."""
    print("🧪 Minimal GCP Logging Test")
    print("=" * 40)
    
    print(f"Project from gcloud: {os.popen('gcloud config get-value project').read().strip()}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    print()
    
    # Test direct StructuredLogHandler
    success1 = test_direct_gcp_logging()
    
    # Test setup_logging() method
    success2 = test_cloud_logging_setup()
    
    print("\n" + "=" * 40)
    print("Results:")
    print(f"   Direct StructuredLogHandler: {'✅' if success1 else '❌'}")
    print(f"   setup_logging() method: {'✅' if success2 else '❌'}")
    print()
    print("Now run: gcloud logging tail")
    print("You should see messages from 'minimal-test' logger")

if __name__ == "__main__":
    main()