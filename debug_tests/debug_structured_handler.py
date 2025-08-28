#!/usr/bin/env python3
"""
Debug why StructuredLogHandler isn't working.
"""

import logging
import time

def test_structured_handler_variations():
    """Test different StructuredLogHandler configurations."""
    
    try:
        from google.cloud import logging as cloud_logging
        from google.cloud.logging.handlers import StructuredLogHandler
        
        client = cloud_logging.Client()
        print(f"Testing with project: {client.project}")
        
        # Test 1: Basic StructuredLogHandler
        print("\n=== Test 1: Basic StructuredLogHandler ===")
        handler1 = StructuredLogHandler(client=client)
        logger1 = logging.getLogger('structured-test-1')
        logger1.setLevel(logging.INFO)
        logger1.handlers.clear()
        logger1.addHandler(handler1)
        logger1.propagate = False  # Don't propagate to root
        
        logger1.info("Test 1: Basic StructuredLogHandler message")
        handler1.flush()
        print("✅ Test 1 sent")
        
        # Test 2: StructuredLogHandler with propagation
        print("\n=== Test 2: StructuredLogHandler with propagation ===")
        handler2 = StructuredLogHandler(client=client)
        logger2 = logging.getLogger('structured-test-2')
        logger2.setLevel(logging.INFO)
        logger2.handlers.clear()
        logger2.addHandler(handler2)
        logger2.propagate = True  # Allow propagation to root
        
        logger2.info("Test 2: StructuredLogHandler with propagation")
        handler2.flush()
        print("✅ Test 2 sent")
        
        # Test 3: Different log name
        print("\n=== Test 3: Different log name ===")
        handler3 = StructuredLogHandler(client=client, name="custom-log")
        logger3 = logging.getLogger('structured-test-3')
        logger3.setLevel(logging.INFO)
        logger3.handlers.clear()
        logger3.addHandler(handler3)
        
        logger3.info("Test 3: Custom log name")
        handler3.flush()
        print("✅ Test 3 sent")
        
        # Test 4: Root logger with StructuredLogHandler
        print("\n=== Test 4: Root logger with StructuredLogHandler ===")
        root_logger = logging.getLogger()
        handler4 = StructuredLogHandler(client=client)
        root_logger.addHandler(handler4)
        
        root_logger.info("Test 4: Root logger with StructuredLogHandler")
        handler4.flush()
        print("✅ Test 4 sent")
        
        # Wait a bit for logs to process
        print("\nWaiting 3 seconds for logs to process...")
        time.sleep(3)
        
        # Cleanup
        for handler in [handler1, handler2, handler3, handler4]:
            try:
                handler.close()
            except:
                pass
        
        print("✅ All tests completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 Debugging StructuredLogHandler")
    print("=" * 50)
    
    test_structured_handler_variations()
    
    print("\n" + "=" * 50)
    print("Now run one of these commands to check for logs:")
    print("1. gcloud beta logging tail")
    print("2. gcloud logging read \"timestamp >= \\\"$(date -u -d '2 minutes ago' --iso-8601)\\\"\" --limit=10")
    print("3. gcloud logging read \"labels.python_logger=\\\"structured-test-1\\\"\" --limit=5")
    print()
    print("Look for messages containing:")
    print("  - 'structured-test-1'")
    print("  - 'structured-test-2'") 
    print("  - 'structured-test-3'")
    print("  - 'Test 4: Root logger'")
    print()
    print("If you see NONE of these, StructuredLogHandler isn't working at all.")

if __name__ == "__main__":
    main()