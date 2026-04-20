"""
Integration Template: How to Integrate IBM DB2 with Any AI Framework

This template shows the pattern for integrating the IBM DB2 AI Connector
with any AI framework. Follow this pattern to create your own integration.
"""

import sys
import os

# Add core module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../core/src'))

from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor, DB2VectorStore
from typing import Any, Dict, List, Optional


# ============================================================================
# STEP 1: Create a DB2 Configuration
# ============================================================================

def create_db2_config() -> DB2Config:
    """Create DB2 configuration from environment or parameters."""
    return DB2Config(
        database=os.getenv("DB2_DATABASE", "SAMPLE"),
        hostname=os.getenv("DB2_HOSTNAME", "localhost"),
        port=int(os.getenv("DB2_PORT", "50000")),
        username=os.getenv("DB2_USERNAME", "db2inst1"),
        password=os.getenv("DB2_PASSWORD", "password")
    )


# ============================================================================
# STEP 2: Create Wrapper Functions for Your Framework
# ============================================================================

class DB2Connector:
    """
    Generic DB2 connector that can be adapted to any framework.
    
    This class provides a clean interface that can be wrapped by
    framework-specific classes (Tools, Agents, Nodes, etc.)
    """
    
    def __init__(self, config: DB2Config):
        """Initialize connector with DB2 configuration."""
        self.config = config
        self.connection_manager = DB2ConnectionManager(config)
    
    def query(self, sql: str, params: Optional[tuple] = None, 
              max_rows: int = 100) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            sql: SQL query string
            params: Optional query parameters
            max_rows: Maximum rows to return
            
        Returns:
            List of dictionaries representing rows
        """
        with self.connection_manager as conn:
            executor = DB2SQLExecutor(conn)
            return executor.execute_query(sql, params, max_rows)
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE and return affected rows.
        
        Args:
            sql: SQL statement
            params: Optional parameters
            
        Returns:
            Number of affected rows
        """
        with self.connection_manager as conn:
            executor = DB2SQLExecutor(conn)
            return executor.execute_update(sql, params)
    
    def batch_execute(self, sql: str, params_list: List[tuple]) -> int:
        """
        Execute batch operations.
        
        Args:
            sql: SQL statement
            params_list: List of parameter tuples
            
        Returns:
            Total affected rows
        """
        with self.connection_manager as conn:
            executor = DB2SQLExecutor(conn)
            return executor.execute_many(sql, params_list)
    
    def vector_search(self, query: str, table_name: str, 
                     embedding_function, k: int = 5) -> List[tuple]:
        """
        Perform vector similarity search.
        
        Args:
            query: Search query text
            table_name: Vector table name
            embedding_function: Function to generate embeddings
            k: Number of results
            
        Returns:
            List of (text, score, metadata) tuples
        """
        with self.connection_manager as conn:
            vector_store = DB2VectorStore(
                connection=conn,
                table_name=table_name,
                embedding_function=embedding_function
            )
            return vector_store.search(query, k=k)
    
    def add_documents(self, texts: List[str], table_name: str,
                     embedding_function, metadatas: Optional[List[Dict]] = None):
        """
        Add documents to vector store.
        
        Args:
            texts: List of text documents
            table_name: Vector table name
            embedding_function: Function to generate embeddings
            metadatas: Optional metadata for each document
        """
        with self.connection_manager as conn:
            vector_store = DB2VectorStore(
                connection=conn,
                table_name=table_name,
                embedding_function=embedding_function
            )
            return vector_store.add_texts(texts, metadatas=metadatas)
    
    def close(self):
        """Close database connection."""
        self.connection_manager.close()


# ============================================================================
# STEP 3: Framework-Specific Adapters (Examples)
# ============================================================================

# Example 1: LangChain Tool
def create_langchain_tool(config: DB2Config):
    """Create a LangChain tool for DB2 queries."""
    try:
        from langchain.agents import Tool
    except ImportError:
        print("LangChain not installed. Install with: pip install langchain")
        return None
    
    connector = DB2Connector(config)
    
    def query_db2(query: str) -> str:
        """Execute SQL query on DB2."""
        try:
            results = connector.query(query)
            return f"Query returned {len(results)} rows: {results}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return Tool(
        name="DB2Query",
        func=query_db2,
        description="Execute SQL queries on IBM DB2 database. "
                   "Input should be a valid SQL query string."
    )


# Example 2: AutoGen Function
def create_autogen_functions(config: DB2Config) -> Dict[str, callable]:
    """Create AutoGen-compatible functions."""
    connector = DB2Connector(config)
    
    def query_db2(query: str, max_rows: int = 100) -> Dict[str, Any]:
        """Execute SQL query."""
        try:
            results = connector.query(query, max_rows=max_rows)
            return {"success": True, "results": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_db2(sql: str) -> Dict[str, Any]:
        """Execute INSERT/UPDATE/DELETE."""
        try:
            affected = connector.execute(sql)
            return {"success": True, "affected_rows": affected}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {
        "query_db2": query_db2,
        "execute_db2": execute_db2,
    }


# Example 3: CrewAI Tool
def create_crewai_tool(config: DB2Config):
    """Create a CrewAI tool for DB2."""
    try:
        from crewai_tools import BaseTool
        from pydantic import BaseModel, Field
    except ImportError:
        print("CrewAI not installed. Install with: pip install crewai crewai-tools")
        return None
    
    connector = DB2Connector(config)
    
    class DB2QueryInput(BaseModel):
        query: str = Field(..., description="SQL query to execute")
        max_rows: int = Field(100, description="Maximum rows to return")
    
    class DB2QueryTool(BaseTool):
        name: str = "DB2 Query"
        description: str = "Execute SQL queries on IBM DB2 database"
        args_schema: type[BaseModel] = DB2QueryInput
        
        def _run(self, query: str, max_rows: int = 100) -> str:
            try:
                results = connector.query(query, max_rows=max_rows)
                return f"Query returned {len(results)} rows: {results}"
            except Exception as e:
                return f"Error: {str(e)}"
    
    return DB2QueryTool()


# Example 4: Generic Callable (for any framework)
def create_generic_callable(config: DB2Config):
    """Create a generic callable that works with any framework."""
    connector = DB2Connector(config)
    
    def db2_query(query: str, **kwargs) -> Any:
        """
        Generic DB2 query function.
        Can be used with any framework that accepts callables.
        """
        max_rows = kwargs.get('max_rows', 100)
        try:
            results = connector.query(query, max_rows=max_rows)
            return {
                "success": True,
                "data": results,
                "count": len(results),
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    return db2_query


# ============================================================================
# STEP 4: Usage Examples
# ============================================================================

def example_usage():
    """Demonstrate how to use the integration."""
    
    print("=" * 70)
    print("IBM DB2 AI Connector - Integration Template")
    print("=" * 70)
    
    # Create configuration
    config = create_db2_config()
    print(f"\n✓ Configuration created for: {config.database}")
    
    # Example 1: Direct usage
    print("\n" + "-" * 70)
    print("Example 1: Direct Usage")
    print("-" * 70)
    
    connector = DB2Connector(config)
    try:
        results = connector.query("SELECT * FROM EMPLOYEE FETCH FIRST 3 ROWS ONLY")
        print(f"✓ Retrieved {len(results)} rows")
    finally:
        connector.close()
    
    # Example 2: Generic callable
    print("\n" + "-" * 70)
    print("Example 2: Generic Callable")
    print("-" * 70)
    
    query_func = create_generic_callable(config)
    result = query_func("SELECT COUNT(*) as total FROM EMPLOYEE")
    print(f"✓ Query result: {result}")
    
    # Example 3: Framework-specific (if available)
    print("\n" + "-" * 70)
    print("Example 3: Framework-Specific Tools")
    print("-" * 70)
    
    # Try LangChain
    langchain_tool = create_langchain_tool(config)
    if langchain_tool:
        print("✓ LangChain tool created")
    
    # Try AutoGen
    autogen_funcs = create_autogen_functions(config)
    print(f"✓ AutoGen functions created: {list(autogen_funcs.keys())}")
    
    # Try CrewAI
    crewai_tool = create_crewai_tool(config)
    if crewai_tool:
        print("✓ CrewAI tool created")
    
    print("\n" + "=" * 70)
    print("✓ Integration template demonstration complete!")
    print("=" * 70)
    print("\nTo integrate with your framework:")
    print("1. Use DB2Connector as the base")
    print("2. Create a wrapper class/function for your framework")
    print("3. Map framework-specific APIs to connector methods")
    print("4. Handle errors appropriately for your framework")


if __name__ == "__main__":
    example_usage()

# Made with Bob
