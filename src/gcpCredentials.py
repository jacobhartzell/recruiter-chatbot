
# Class definition for credentialClass

import json
import logging
import os
import tempfile
import streamlit as st

class GCPCredentials:
    def __init__(self):
        try:
            from google.cloud import logging as cloud_logging
            from google.oauth2 import service_account
            self.gcp_logging_available = True
            self.logger =logging.getLogger(__name__)
        except ImportError:
            self.gcp_logging_available = False


    def streamlit_credentials_available(self):
        """Check and return Streamlit-based GCP credentials if available."""
        try:
            # Only try to access secrets if Streamlit is properly initialized
            if hasattr(st, 'secrets') and ('gcp_service_account' in st.secrets):
                return True
        except (ImportError, AttributeError, FileNotFoundError):
            # Streamlit not available or secrets not configured - this is fine
            self.logger.info("Streamlit not available or GCP credentials not found in secrets")
        finally:
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
            return True

        if self.streamlit_credentials_available():
            return True

        # Check if running in GCP by trying to access metadata
        try:
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
        # Try environment variable with JSON content first
        gcp_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if gcp_json:
            try:
                service_account_info = json.loads(gcp_json)
                return service_account.Credentials.from_service_account_info(service_account_info)
            except (json.JSONDecodeError, ValueError) as e:
                # SECURITY: Don't log the actual JSON content or detailed error
                self.logger.warning("Invalid GCP JSON credentials format")
        if self.streamlit_credentials_available():
            return self._get_streamlit_credentials()

        return None
    
    def _get_streamlit_credentials(self):
        if self.streamlit_credentials_available() and self.gcp_logging_available:
            return service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
        else:
            return None 