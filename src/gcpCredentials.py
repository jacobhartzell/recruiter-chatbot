
# Class definition for credentialClass

import json
import logging
import os
import tempfile
import streamlit as st

class GCPCredentials:
    def __init__(self):
        # Ensure a module logger is always available
        self.logger = logging.getLogger(__name__)

        try:
            from google.cloud import logging as cloud_logging
            from google.oauth2 import service_account
            self.gcp_logging_available = True
        except ImportError:
            self.gcp_logging_available = False


    def streamlit_credentials_available(self):
        """Check and return Streamlit-based GCP credentials if available."""
        try:
            # Only try to access secrets if Streamlit is properly initialized
            if hasattr(st, 'secrets'):
                secret_keys = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
                if 'gcp_service_account' in st.secrets:
                    return True
        except (ImportError, AttributeError, FileNotFoundError) as e:
            # Streamlit not available or secrets not configured - this is fine
            pass
        
        return False
    
    # This method should check to see if the credentials are available in the environment
    def gcp_credentials_available(self) -> bool:
        """Determine if GCP logging should be used."""
        # Use GCP logging if:
        # 1. Running in GCP environment (detected by metadata server)
        # 2. Or explicitly enabled via environment variable
        # 3. Or credentials are available
        
        if os.getenv('USE_GCP_LOGGING', '').lower() == 'false':
            self.logger.warning("Checking credentials, but GCP logging disabled")
            return False
        
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            self.logger.info("GCP credentials found in environment variable")
            return True

        if self.streamlit_credentials_available():
            self.logger.info("Streamlit GCP credentials found")
            return True

        # Check if running in GCP by trying to access metadata
        try:
            self.logger.info("Checking GCP metadata")
            import requests
            response = requests.get(
                'http://metadata.google.internal/computeMetadata/v1/project/project-id',
                headers={'Metadata-Flavor': 'Google'},
                timeout=1
            )
            return response.status_code == 200
        except:
            return False

    def get_gcp_credentials(self):
        """Get GCP credentials from various sources."""
        # Try environment variable with streamlit content first
        if self.streamlit_credentials_available():
            return self._get_streamlit_credentials()

        gcp_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if gcp_json:
            try:
                # Import locally to avoid hard dependency at module import time
                from google.oauth2 import service_account
                service_account_info = json.loads(gcp_json)
                return service_account.Credentials.from_service_account_info(service_account_info)
            except (json.JSONDecodeError, ValueError) as e:
                # SECURITY: Don't log the actual JSON content or detailed error
                self.logger.warning("Invalid GCP JSON credentials format")

        return None
    
    def _get_streamlit_credentials(self):
        if self.streamlit_credentials_available() and self.gcp_logging_available:
            from google.oauth2 import service_account
            # Add required scopes for Vertex AI
            scopes = [
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/logging.write'
            ]
            return service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes=scopes
                )
        else:
            return None 