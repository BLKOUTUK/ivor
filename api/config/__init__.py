"""
Configuration module for IVOR backend
"""

from .settings import settings, get_database_url, is_production, get_cors_origins

__all__ = ["settings", "get_database_url", "is_production", "get_cors_origins"]