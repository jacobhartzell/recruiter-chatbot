"""
Test logging functionality for the recruiter chatbot.
"""

import pytest
import os
import tempfile
import yaml
import json
from unittest.mock import patch, Mock
from datetime import datetime

# Add src directory to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.logger import GCPLogger, get_logger


class TestGCPLogger:
    """Test GCP logging functionality."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        config = {
            'logging': {
                'use_gcp_logging': False,
                'log_level': 'INFO',
                'log_file': './test_logs/test_chatbot.log',
                'environment': 'test',
                'service_name': 'test-recruiter-chatbot'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            return f.name

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, 'test_logs')
            os.makedirs(log_dir, exist_ok=True)
            yield log_dir

    def test_logger_initialization_with_config(self, temp_config_file):
        """Test logger initializes correctly with config file."""
        logger = GCPLogger(config_path=temp_config_file)
        
        assert logger.service_name == 'test-recruiter-chatbot'
        assert logger.environment == 'test'
        assert logger.config['logging']['use_gcp_logging'] is False
        
        # Cleanup
        os.unlink(temp_config_file)

    def test_logger_initialization_fallback_config(self):
        """Test logger initializes with fallback config when file not found."""
        logger = GCPLogger(config_path='nonexistent_config.yaml')
        
        assert logger.service_name == 'recruiter-chatbot'
        assert logger.environment == 'development'
        assert logger.config['logging']['use_gcp_logging'] is False

    def test_local_logging_setup(self, temp_config_file, temp_log_dir):
        """Test local logging setup works correctly."""
        # Update config to use temp log dir
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['logging']['log_file'] = os.path.join(temp_log_dir, 'test.log')
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config, f)
        
        logger = GCPLogger(config_path=temp_config_file)
        logger.info("Test message")
        
        # Check log file was created and contains message
        log_file = config['logging']['log_file']
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Test message" in log_content
            assert "test-recruiter-chatbot" in log_content
        
        # Cleanup
        os.unlink(temp_config_file)

    def test_chat_interaction_logging(self, temp_config_file, temp_log_dir):
        """Test chat interaction logging."""
        # Setup config with temp log dir
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['logging']['log_file'] = os.path.join(temp_log_dir, 'chat.log')
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config, f)
        
        logger = GCPLogger(config_path=temp_config_file)
        
        # Log a chat interaction
        user_input = "What is your experience?"
        bot_response = "I have 5 years of experience in software development."
        metadata = {"session_id": "test123", "model": "gemini"}
        
        logger.log_chat_interaction(user_input, bot_response, metadata)
        
        # Check log file contains structured data
        log_file = config['logging']['log_file']
        with open(log_file, 'r') as f:
            log_content = f.read()
            
        # Parse the JSON log entry
        log_lines = [line for line in log_content.split('\n') if line.strip()]
        assert len(log_lines) > 0
        
        # Find the chat interaction log line
        chat_log = None
        for line in log_lines:
            if '"event_type": "chat_interaction"' in line:
                # Extract JSON from the log line
                json_start = line.find('{"event_type"')
                if json_start != -1:
                    json_str = line[json_start:]
                    chat_log = json.loads(json_str)
                    break
        
        assert chat_log is not None
        assert chat_log['event_type'] == 'chat_interaction'
        assert chat_log['user_input'] == user_input
        assert chat_log['bot_response'] == bot_response
        assert chat_log['metadata']['session_id'] == 'test123'
        assert chat_log['service'] == 'test-recruiter-chatbot'
        assert chat_log['environment'] == 'test'
        
        # Cleanup
        os.unlink(temp_config_file)

    def test_rate_limit_event_logging(self, temp_config_file, temp_log_dir):
        """Test rate limit event logging."""
        # Setup config
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['logging']['log_file'] = os.path.join(temp_log_dir, 'rate_limit.log')
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config, f)
        
        logger = GCPLogger(config_path=temp_config_file)
        
        # Log rate limit event
        details = {
            "limit_type": "per_minute",
            "limit_value": 10,
            "current_count": 11,
            "session_id": "test456"
        }
        
        logger.log_rate_limit_event("exceeded", details)
        
        # Check log file
        log_file = config['logging']['log_file']
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert '"event_type": "rate_limit"' in log_content
        assert '"rate_limit_event": "exceeded"' in log_content
        assert '"limit_type": "per_minute"' in log_content
        
        # Cleanup
        os.unlink(temp_config_file)

    def test_system_event_logging(self, temp_config_file, temp_log_dir):
        """Test system event logging."""
        # Setup config
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['logging']['log_file'] = os.path.join(temp_log_dir, 'system.log')
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config, f)
        
        logger = GCPLogger(config_path=temp_config_file)
        
        # Log system event
        logger.log_system_event(
            "rag_initialization",
            "RAG system started successfully",
            level="INFO",
            metadata={"model": "gemini-2.0-flash-001"}
        )
        
        # Check log file
        log_file = config['logging']['log_file']
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert '"event_type": "system_event"' in log_content
        assert '"system_event_type": "rag_initialization"' in log_content
        assert '"message": "RAG system started successfully"' in log_content
        
        # Cleanup
        os.unlink(temp_config_file)

    def test_get_logger_singleton(self):
        """Test get_logger returns the same instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        
        assert logger1 is logger2

    @patch('src.logger.cloud_logging')
    def test_gcp_logging_enabled(self, mock_cloud_logging, temp_config_file):
        """Test GCP logging when enabled."""
        # Setup config with GCP enabled
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['logging']['use_gcp_logging'] = True
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Mock GCP client
        mock_client = Mock()
        mock_cloud_logging.Client.return_value = mock_client
        
        with patch('src.logger.GCP_LOGGING_AVAILABLE', True):
            with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': 'test.json'}):
                logger = GCPLogger(config_path=temp_config_file)
                
                # Verify GCP client was initialized
                mock_cloud_logging.Client.assert_called_once()
                mock_client.setup_logging.assert_called_once()
        
        # Cleanup
        os.unlink(temp_config_file)


if __name__ == "__main__":
    pytest.main([__file__])