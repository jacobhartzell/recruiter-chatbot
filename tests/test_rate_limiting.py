"""
Test rate limiting functionality for the Streamlit app.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
from unittest.mock import Mock, patch
import yaml

# Import the rate limiting function
from streamlit_app import check_rate_limit, load_config


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            'rate_limiting': {
                'max_requests_per_minute': 3,
                'max_requests_per_hour': 10
            }
        }

    @pytest.fixture
    def mock_session_state(self):
        """Mock Streamlit session state."""
        class MockSessionState:
            def __init__(self):
                self.request_times = []
            
            def __contains__(self, key):
                return hasattr(self, key)
            
            def __getitem__(self, key):
                return getattr(self, key)
            
            def __setitem__(self, key, value):
                setattr(self, key, value)
        
        return MockSessionState()

    def test_first_request_allowed(self, mock_config, mock_session_state):
        """Test that first request is always allowed."""
        with patch('streamlit_app.st.session_state', mock_session_state):
            is_allowed, error_message = check_rate_limit(mock_config)
            assert is_allowed is True
            assert error_message is None
            assert len(mock_session_state.request_times) == 1

    def test_rate_limit_per_minute_exceeded(self, mock_config, mock_session_state):
        """Test rate limit per minute is enforced."""
        current_time = datetime.now()
        
        # Add requests that exceed per-minute limit
        mock_session_state.request_times = [
            current_time - timedelta(seconds=10),
            current_time - timedelta(seconds=20),
            current_time - timedelta(seconds=30)
        ]
        
        with patch('streamlit_app.st.session_state', mock_session_state):
            is_allowed, error_message = check_rate_limit(mock_config)
            assert is_allowed is False
            assert "Maximum 3 requests per minute" in error_message

    def test_rate_limit_per_hour_exceeded(self, mock_config, mock_session_state):
        """Test rate limit per hour is enforced."""
        current_time = datetime.now()
        
        # Add requests that exceed per-hour limit (but not per-minute)
        mock_session_state.request_times = []
        for i in range(10):
            # Spread requests over different minutes to avoid per-minute limit
            mock_session_state.request_times.append(
                current_time - timedelta(minutes=i*5)
            )
        
        with patch('streamlit_app.st.session_state', mock_session_state):
            is_allowed, error_message = check_rate_limit(mock_config)
            assert is_allowed is False
            assert "Maximum 10 requests per hour" in error_message

    def test_old_requests_cleaned_up(self, mock_config, mock_session_state):
        """Test that old requests are cleaned up."""
        current_time = datetime.now()
        
        # Add old requests (older than 1 hour) and recent requests
        mock_session_state.request_times = [
            current_time - timedelta(hours=2),  # Should be cleaned up
            current_time - timedelta(hours=1, minutes=30),  # Should be cleaned up
            current_time - timedelta(minutes=30)  # Should remain
        ]
        
        with patch('streamlit_app.st.session_state', mock_session_state):
            is_allowed, error_message = check_rate_limit(mock_config)
            assert is_allowed is True
            assert error_message is None
            # Should have 1 old request + 1 new request = 2 total
            assert len(mock_session_state.request_times) == 2

    def test_config_loading(self):
        """Test that configuration loads correctly."""
        config = load_config()
        assert 'rate_limiting' in config
        assert 'max_requests_per_minute' in config['rate_limiting']
        assert 'max_requests_per_hour' in config['rate_limiting']
        assert isinstance(config['rate_limiting']['max_requests_per_minute'], int)
        assert isinstance(config['rate_limiting']['max_requests_per_hour'], int)


if __name__ == "__main__":
    pytest.main([__file__])