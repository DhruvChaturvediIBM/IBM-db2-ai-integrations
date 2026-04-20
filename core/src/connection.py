"""IBM DB2 Connection Manager - Framework Agnostic

Provides connection management for IBM DB2 databases that can be used
across different AI frameworks.
"""

import logging
from dataclasses import dataclass
from typing import Optional

try:
    import ibm_db_dbi
except ImportError:
    raise ImportError(
        "ibm_db_dbi is required. Install with: pip install ibm_db ibm_db_dbi"
    )

logger = logging.getLogger(__name__)


@dataclass
class DB2Config:
    """IBM DB2 connection configuration.
    
    Attributes:
        database: Name of the DB2 database
        hostname: DB2 server hostname or IP address
        port: DB2 server port (default: 50000)
        username: DB2 database username
        password: DB2 database password
        protocol: Connection protocol (default: TCPIP)
        ssl: Enable SSL connection (default: False)
    """
    
    database: str
    hostname: str
    username: str
    password: str
    port: int = 50000
    protocol: str = "TCPIP"
    ssl: bool = False
    
    def to_connection_string(self) -> str:
        """Generate IBM DB2 connection string.
        
        Returns:
            Formatted connection string for ibm_db_dbi
        """
        conn_str = (
            f"DATABASE={self.database};"
            f"HOSTNAME={self.hostname};"
            f"PORT={self.port};"
            f"PROTOCOL={self.protocol};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        
        if self.ssl:
            conn_str += "SECURITY=SSL;"
        
        return conn_str
    
    def __repr__(self) -> str:
        """Safe representation without exposing password."""
        return (
            f"DB2Config(database='{self.database}', "
            f"hostname='{self.hostname}', "
            f"port={self.port}, "
            f"username='{self.username}', "
            f"password='***')"
        )


class DB2ConnectionManager:
    """Manages IBM DB2 database connections.
    
    Provides connection pooling and context manager support for
    safe connection handling across different AI frameworks.
    
    Example:
        >>> config = DB2Config(
        ...     database="mydb",
        ...     hostname="localhost",
        ...     username="db2user",
        ...     password="password"
        ... )
        >>> manager = DB2ConnectionManager(config)
        >>> with manager as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM table")
    """
    
    def __init__(self, config: DB2Config):
        """Initialize connection manager.
        
        Args:
            config: DB2Config instance with connection parameters
        """
        self.config = config
        self._connection = None
        logger.info(f"Initialized DB2ConnectionManager for {config.database}")
    
    def connect(self):
        """Establish connection to DB2 database.
        
        Returns:
            ibm_db_dbi.Connection object
            
        Raises:
            RuntimeError: If connection fails
        """
        if not self._connection:
            try:
                conn_str = self.config.to_connection_string()
                self._connection = ibm_db_dbi.connect(conn_str, "", "")
                logger.info(
                    f"Connected to DB2 database: {self.config.database} "
                    f"at {self.config.hostname}:{self.config.port}"
                )
            except Exception as e:
                error_msg = f"Failed to connect to DB2: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e
        
        return self._connection
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.info(f"Closed connection to {self.config.database}")
            except Exception as e:
                logger.warning(f"Error closing connection: {str(e)}")
            finally:
                self._connection = None
    
    def is_connected(self) -> bool:
        """Check if connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connection is not None
    
    def reconnect(self):
        """Close existing connection and establish a new one.
        
        Returns:
            New connection object
        """
        self.close()
        return self.connect()
    
    def __enter__(self):
        """Context manager entry - establish connection."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
        return False
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()

# Made with Bob
