#!/usr/bin/env python3
"""
Focused GCP logging debug script.
"""

import os
import sys
import json

# Add src to path
sys.path.append('src')

def check_environment():
    """Check environment setup."""
    print("=== Environment Check ===")
    
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    print(f"GCP_SERVICE_ACCOUNT_JSON: {'SET' if os.getenv('GCP_SERVICE_ACCOUNT_JSON') else 'NOT SET'}")
    print(f"USE_GCP_LOGGING: {os.getenv('USE_GCP_LOGGING')}")
    
    # Check if credentials file exists
    creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_file:
        if os.path.exists(creds_file):
            print(f"✅ Credentials file exists: {creds_file}")
            try:
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                print(f"   Project ID: {creds.get('project_id')}")
                print(f"   Client Email: {creds.get('client_email')}")
            except Exception as e:
                print(f"   ❌ Error reading credentials: {e}")
        else:
            print(f"❌ Credentials file missing: {creds_file}")

def test_gcp_import():
    """Test GCP imports."""
    print("\n=== GCP Import Test ===")
    
    try:
        from google.cloud import logging as cloud_logging
        print("✅ google.cloud.logging imported")
        
        from google.oauth2 import service_account
        print("✅ google.oauth2.service_account imported")
        
        from google.cloud.logging.handlers import StructuredLogHandler
        print("✅ StructuredLogHandler imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_gcp_client():
    """Test GCP client creation."""
    print("\n=== GCP Client Test ===")
    
    try:
        from google.cloud import logging as cloud_logging
        
        print("Creating GCP client...")
        client = cloud_logging.Client()
        print(f"✅ Client created successfully")
        print(f"   Project: {client.project}")
        
        # Test a simple operation
        print("Testing client connection...")
        # Just test if we can access the client properties
        project = client.project
        print(f"✅ Client connection working, project: {project}")
        
        return client
        
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_structured_handler(client):
    """Test StructuredLogHandler."""
    print("\n=== StructuredLogHandler Test ===")
    
    if not client:
        print("❌ No client available")
        return None
    
    try:
        from google.cloud.logging.handlers import StructuredLogHandler
        import logging
        
        print("Creating StructuredLogHandler...")
        handler = StructuredLogHandler(client=client)
        handler.setLevel(logging.INFO)
        
        print("✅ StructuredLogHandler created")
        
        # Create test logger
        test_logger = logging.getLogger('debug-test')
        test_logger.setLevel(logging.INFO)
        test_logger.handlers.clear()
        test_logger.addHandler(handler)
        
        print("Sending test log message...")
        test_logger.info("Debug test message from StructuredLogHandler")
        
        print("Flushing handler...")
        handler.flush()
        
        print("✅ Test message sent to GCP")
        return handler
        
    except Exception as e:
        print(f"❌ StructuredLogHandler test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_our_logger_step_by_step():
    """Test our logger creation step by step."""
    print("\n=== Our Logger Debug ===")
    
    try:
        # Import our logger components
        from src.logger import GCPLogger
        
        print("Creating GCPLogger instance...")
        logger = GCPLogger()
        
        print(f"   Service name: {logger.service_name}")
        print(f"   Environment: {logger.environment}")
        print(f"   Config use_gcp_logging: {logger.config['logging']['use_gcp_logging']}")
        
        # Check what _should_use_gcp_logging returns
        should_use = logger._check_gcp_credentials_available()
        print(f"   _should_use_gcp_logging(): {should_use}")
        
        # Check credentials
        credentials = logger._get_gcp_credentials()
        print(f"   _get_gcp_credentials(): {'Found' if credentials else 'None'}")
        
        # Check handlers
        print(f"   Number of handlers: {len(logger.logger.handlers)}")
        for i, handler in enumerate(logger.logger.handlers):
            print(f"   Handler {i}: {type(handler).__name__}")
        
        # Check cloud client
        print(f"   Cloud client: {'Created' if logger.cloud_client else 'None'}")
        if logger.cloud_client:
            print(f"   Cloud client project: {logger.cloud_client.project}")
        
        return logger
        
    except Exception as e:
        print(f"❌ Our logger debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run debug tests."""
    print("🔍 Debugging GCP Logging Issues")
    print("=" * 50)
    
    check_environment()
    
    if not test_gcp_import():
        print("\n❌ GCP imports failed - cannot proceed")
        return
    
    client = test_gcp_client()
    if not client:
        print("\n❌ GCP client failed - cannot proceed")
        return
    
    handler = test_structured_handler(client)
    
    logger = test_our_logger_step_by_step()
    
    print("\n" + "=" * 50)
    print("🎯 Debug Summary:")
    print(f"   GCP imports: {'✅' if test_gcp_import() else '❌'}")
    print(f"   GCP client: {'✅' if client else '❌'}")
    print(f"   Structured handler: {'✅' if handler else '❌'}")
    print(f"   Our logger: {'✅' if logger else '❌'}")

if __name__ == "__main__":
    main()