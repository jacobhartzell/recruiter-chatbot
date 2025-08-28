#!/usr/bin/env python3
"""
Test CloudLoggingHandler properly configured to avoid threading issues.
"""

import logging
import time

def test_cloud_logging_handler():
    """Test CloudLoggingHandler with proper configuration."""
    
    try:
        from google.cloud import logging as cloud_logging
        from google.cloud.logging.handlers import CloudLoggingHandler
        
        client = cloud_logging.Client()
        print(f"Testing CloudLoggingHandler with project: {client.project}")
        
        # Create CloudLoggingHandler with specific configuration
        handler = CloudLoggingHandler(
            client=client,
            name="recruiter-chatbot",  # Explicit log name
            # Don't set resource - let it auto-detect
        )
        
        # Create our logger
        logger = logging.getLogger('recruiter-chatbot-test')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False  # Prevent double logging
        
        print("Sending test messages...")
        
        # Send test messages
        logger.info("CloudLoggingHandler test: Basic message")
        logger.warning("CloudLoggingHandler test: Warning message")
        
        # Send structured data
        import json
        structured = {
            "event_type": "test",
            "service": "recruiter-chatbot-test", 
            "message": "Structured test data",
            "metadata": {"test": True}
        }
        logger.info(json.dumps(structured))
        
        # Explicit flush
        handler.flush()
        print("✅ Messages sent and flushed")
        
        # Wait for processing
        time.sleep(2)
        
        # Clean shutdown to avoid threading issues
        handler.close()
        print("✅ Handler closed cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ CloudLoggingHandler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_with_name():
    """Test StructuredLogHandler with explicit name."""
    
    try:
        from google.cloud import logging as cloud_logging
        from google.cloud.logging.handlers import StructuredLogHandler
        
        client = cloud_logging.Client()
        print(f"\nTesting StructuredLogHandler with explicit name...")
        
        # Create with explicit name (this was missing!)
        handler = StructuredLogHandler(
            client=client,
            name="recruiter-chatbot-structured"  # This was the missing piece!
        )
        
        logger = logging.getLogger('structured-with-name')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False
        
        print("Sending StructuredLogHandler messages...")
        
        logger.info("StructuredLogHandler with name: Test message")
        logger.error("StructuredLogHandler with name: Error message")
        
        handler.flush()
        time.sleep(2)
        handler.close()
        
        print("✅ StructuredLogHandler with name completed")
        return True
        
    except Exception as e:
        print(f"❌ StructuredLogHandler with name failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing Proper Cloud Logging Handlers")
    print("=" * 50)
    
    # Test CloudLoggingHandler (recommended approach)
    success1 = test_cloud_logging_handler()
    
    # Test StructuredLogHandler with proper name
    success2 = test_structured_with_name()
    
    print("\n" + "=" * 50)
    print("Results:")
    print(f"   CloudLoggingHandler: {'✅' if success1 else '❌'}")
    print(f"   StructuredLogHandler (with name): {'✅' if success2 else '❌'}")
    print()
    print("Check logs with:")
    print('gcloud logging read "timestamp >= \\"$(date -u -d \'2 minutes ago\' --iso-8601)\\"" --limit=20')
    print()
    print("Look for log names:")
    print("  - projects/YOUR_PROJECT/logs/recruiter-chatbot")
    print("  - projects/YOUR_PROJECT/logs/recruiter-chatbot-structured")

if __name__ == "__main__":
    main()