"""
Utility functions for the recruiter chatbot.

This module contains shared utilities used across the application.
"""

import sys
import os


def fix_sqlite_compatibility():
    """
    Apply SQLite compatibility fix for Streamlit Cloud.
    
    This function attempts to use pysqlite3 instead of the default sqlite3
    module, which is necessary for compatibility with Streamlit Cloud deployment.
    """
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        # pysqlite3 not available, use default sqlite3
        pass
    # Ensure we do not force any alternative DB backend
