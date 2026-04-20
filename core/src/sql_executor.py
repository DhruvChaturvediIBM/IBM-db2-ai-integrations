"""IBM DB2 SQL Executor - Framework Agnostic

Provides SQL query execution capabilities for IBM DB2 databases
that can be used across different AI frameworks.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class DB2SQLExecutor:
    """Execute SQL queries on IBM DB2 database.
    
    Provides methods for executing SELECT, INSERT, UPDATE, DELETE queries
    with proper error handling and result formatting.
    
    Example:
        >>> from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor
        >>> config = DB2Config(database="mydb", hostname="localhost", 
        ...                    username="user", password="pass")
        >>> with DB2ConnectionManager(config) as conn:
        ...     executor = DB2SQLExecutor(conn)
        ...     results = executor.execute_query("SELECT * FROM table LIMIT 10")
        ...     print(f"Retrieved {len(results)} rows")
    """
    
    def __init__(self, connection):
        """Initialize SQL executor.
        
        Args:
            connection: Active ibm_db_dbi connection object
        """
        self.connection = connection
        logger.debug("Initialized DB2SQLExecutor")
    
    def execute_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        max_rows: int = 100
    ) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dictionaries.
        
        Args:
            query: SQL SELECT query to execute
            params: Optional query parameters for parameterized queries
            max_rows: Maximum number of rows to return (default: 100)
            
        Returns:
            List of dictionaries where each dict represents a row
            
        Raises:
            RuntimeError: If query execution fails
            
        Example:
            >>> results = executor.execute_query(
            ...     "SELECT * FROM users WHERE age > ?",
            ...     params=(25,),
            ...     max_rows=50
            ... )
        """
        cursor = self.connection.cursor()
        try:
            logger.debug(f"Executing query: {query[:100]}...")
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if query returns results (SELECT)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchmany(max_rows)
                
                # Convert to list of dictionaries
                results = [
                    dict(zip(columns, row))
                    for row in rows
                ]
                
                logger.info(f"Query returned {len(results)} rows")
                return results
            
            # Query doesn't return results
            logger.info("Query executed successfully (no results)")
            return []
            
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        finally:
            cursor.close()
    
    def execute_update(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None
    ) -> int:
        """Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL INSERT/UPDATE/DELETE query to execute
            params: Optional query parameters for parameterized queries
            
        Returns:
            Number of rows affected
            
        Raises:
            RuntimeError: If query execution fails
            
        Example:
            >>> affected = executor.execute_update(
            ...     "UPDATE users SET status = ? WHERE id = ?",
            ...     params=('active', 123)
            ... )
            >>> print(f"Updated {affected} rows")
        """
        cursor = self.connection.cursor()
        try:
            logger.debug(f"Executing update: {query[:100]}...")
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            
            logger.info(f"Query affected {affected_rows} rows")
            return affected_rows
            
        except Exception as e:
            self.connection.rollback()
            error_msg = f"Error executing update: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        finally:
            cursor.close()
    
    def execute_many(
        self,
        query: str,
        params_list: List[Union[Tuple, List]]
    ) -> int:
        """Execute same query multiple times with different parameters.
        
        Useful for bulk inserts or updates.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples/lists
            
        Returns:
            Total number of rows affected
            
        Raises:
            RuntimeError: If query execution fails
            
        Example:
            >>> data = [
            ...     ('John', 30, 'john@example.com'),
            ...     ('Jane', 25, 'jane@example.com'),
            ... ]
            >>> affected = executor.execute_many(
            ...     "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
            ...     data
            ... )
        """
        cursor = self.connection.cursor()
        try:
            logger.debug(f"Executing batch query with {len(params_list)} parameter sets")
            
            cursor.executemany(query, params_list)
            self.connection.commit()
            affected_rows = cursor.rowcount
            
            logger.info(f"Batch query affected {affected_rows} rows")
            return affected_rows
            
        except Exception as e:
            self.connection.rollback()
            error_msg = f"Error executing batch query: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        finally:
            cursor.close()
    
    def execute_raw(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        fetch_all: bool = False
    ) -> Any:
        """Execute raw SQL query and return cursor results.
        
        For advanced use cases where you need direct cursor access.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            fetch_all: If True, fetch all results; otherwise return cursor
            
        Returns:
            Query results or cursor object
            
        Raises:
            RuntimeError: If query execution fails
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_all and cursor.description:
                results = cursor.fetchall()
                cursor.close()
                return results
            
            return cursor
            
        except Exception as e:
            cursor.close()
            error_msg = f"Error executing raw query: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            cursor.close()
            return True
        except Exception as e:
            if "SQL0204N" in str(e):  # Table not found error
                return False
            raise
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dictionaries with column information
        """
        query = """
            SELECT 
                COLNAME as column_name,
                TYPENAME as data_type,
                LENGTH as length,
                NULLS as nullable
            FROM SYSCAT.COLUMNS
            WHERE TABNAME = ?
            ORDER BY COLNO
        """
        return self.execute_query(query, params=(table_name.upper(),))

# Made with Bob
