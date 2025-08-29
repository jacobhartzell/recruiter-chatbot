"""
Google Cloud Platform logging integration for the recruiter chatbot.
"""

import logging
import json
import os
import yaml
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import logging as cloud_logging
from google.oauth2 import service_account
from src.gcpCredentials import GCPCredentials




class GCPLogger:
    """Enhanced logger with Google Cloud Platform integration."""
    
    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize the GCP logger.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.service_name = self.config['logging']['service_name']
        self.environment = self.config['logging']['environment']
        self.logger = logging.getLogger(self.service_name)
        self.cloud_client = None
        self.cloud_handler = None
        self.gcp_credentials = GCPCredentials()

        # Setup logging based on configuration
        self._setup_logging()
        
        # Register cleanup on exit
        import atexit
        atexit.register(self._cleanup)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Fallback configuration
            return {
                'logging': {
                    'use_gcp_logging': False,
                    'log_level': 'INFO',
                    'log_file': './logs/chatbot.log',
                    'environment': 'development',
                    'service_name': 'recruiter-chatbot'
                }
            }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set logging level from config
        log_level = self.config['logging']['log_level'].upper()
        self.logger.setLevel(getattr(logging, log_level))
        
        # Check if GCP logging should be used
        use_gcp = self.config['logging'].get('use_gcp_logging', False)
        
        # Always set up local logging first
        self._setup_local_logging()
        
        # Add GCP logging if enabled  
        if use_gcp:
            if not self.gcp_credentials.gcp_logging_available:
                self.logger.error("GCP logging requested but google-cloud-logging not available")
                return
            
            if not self.gcp_credentials.gcp_credentials_available():
                self.logger.warning("GCP logging enabled in config but no credentials found")
                return
            try:
                # Initialize client with credentials if available
                credentials = self.gcp_credentials.get_gcp_credentials()
                if credentials:
                    self.cloud_client = cloud_logging.Client(credentials=credentials)
                else:
                    self.cloud_client = cloud_logging.Client()
                
                # Use CloudLoggingHandler with explicit name - this works reliably
                from google.cloud.logging.handlers import CloudLoggingHandler
                
                cloud_handler = CloudLoggingHandler(
                    client=self.cloud_client,
                    name=self.service_name  # Critical: explicit log name
                )
                cloud_handler.setLevel(getattr(logging, log_level))
                
                # Add structured fields for all log messages
                cloud_handler.addFilter(self._add_structured_fields)
                self.logger.addHandler(cloud_handler)
                self.cloud_handler = cloud_handler  # Keep reference for cleanup
                
                # Prevent double logging
                self.logger.propagate = False
                
                self.logger.info("GCP Cloud Logging initialized successfully (dual logging mode)")
                
            except Exception as e:
                # SECURITY: Never log the full exception as it may contain credentials
                self.logger.warning("Failed to initialize GCP logging: Authentication or connection error")
                self.logger.info("Continuing with local logging only")


    
    def _add_structured_fields(self, record):
        """Add structured fields to log records for GCP."""
        record.service = self.service_name
        record.environment = self.environment
        record.timestamp = datetime.utcnow().isoformat()
        return True
    
    def _cleanup(self):
        """Clean up logging handlers to avoid shutdown issues."""
        try:
            # Force flush and close cloud handler
            if self.cloud_handler:
                self.cloud_handler.flush()
                # Remove from logger to prevent further use
                self.logger.removeHandler(self.cloud_handler)
                self.cloud_handler.close()
                self.cloud_handler = None
            
            # Close client connection
            if self.cloud_client:
                try:
                    self.cloud_client.close()
                except:
                    pass
                self.cloud_client = None
                
        except Exception:
            pass  # Ignore cleanup errors during shutdown
    
    def _setup_local_logging(self):
        """Setup local console and file logging."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.logger.level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - try multiple locations
        log_files_to_try = [
            self.config['logging']['log_file'],  # From config
            '/var/log/chatbot.log',               # System log location
            './logs/chatbot.log',                 # Local fallback
            '/tmp/chatbot.log'                    # Last resort
        ]
        
        file_handler_added = False
        for log_file in log_files_to_try:
            try:
                # Create log directory if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(self.logger.level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                file_handler_added = True
                self.logger.info(f"Local logging initialized: {log_file}")
                break
                
            except (PermissionError, FileNotFoundError, OSError) as e:
                # Try next location
                continue
        
        if not file_handler_added:
            self.logger.warning("Could not create file handler, using console logging only")
    
    def log_chat_interaction(self, user_input: str, bot_response: str, 
                           metadata: Optional[Dict[str, Any]] = None):
        """
        Log a chat interaction with structured data.
        
        Args:
            user_input: User's input message
            bot_response: Bot's response message
            metadata: Additional metadata (session_id, user_id, etc.)
        """
        # Simplified payload - GCP already has timestamp and service info
        log_data = {
            "event_type": "chat_interaction",
            "user_input": user_input,
            "bot_response": bot_response
        }
        
        # Add metadata if provided (session_id, model, etc.)
        if metadata:
            log_data.update(metadata)
        
        self.logger.info(json.dumps(log_data))
    
    def log_rate_limit_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log rate limiting events.
        
        Args:
            event_type: Type of rate limit event (exceeded, warning, etc.)
            details: Details about the event
        """
        log_data = {
            "event_type": "rate_limit",
            "rate_limit_event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "service": self.service_name,
            "environment": self.environment
        }
        
        if event_type == "exceeded":
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def log_system_event(self, event_type: str, message: str, 
                        level: str = "INFO", metadata: Optional[Dict[str, Any]] = None):
        """
        Log system events with structured data.
        
        Args:
            event_type: Type of system event
            message: Event message
            level: Log level (INFO, WARNING, ERROR)
            metadata: Additional metadata
        """
        log_data = {
            "event_type": "system_event",
            "system_event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "service": self.service_name,
            "environment": self.environment
        }
        
        if metadata:
            log_data["metadata"] = metadata
        
        log_level = getattr(self.logger, level.lower())
        log_level(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def flush(self):
        """Manually flush all log handlers."""
        try:
            if self.cloud_handler:
                self.cloud_handler.flush()
            for handler in self.logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
        except Exception:
            pass


# Global logger instance
_logger_instance = None

def get_logger() -> GCPLogger:
    """Get the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = GCPLogger()
    return _logger_instance