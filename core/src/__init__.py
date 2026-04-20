"""IBM DB2 AI Integration - Core Module

A framework-agnostic library for integrating IBM DB2 with AI frameworks.
Provides connection management, SQL execution, and vector store operations.
"""

from .connection import DB2Config, DB2ConnectionManager
from .sql_executor import DB2SQLExecutor
from .vector_store import DB2VectorStore

__version__ = "1.0.0"

__all__ = [
    "DB2Config",
    "DB2ConnectionManager",
    "DB2SQLExecutor",
    "DB2VectorStore",
]

# Made with Bob
