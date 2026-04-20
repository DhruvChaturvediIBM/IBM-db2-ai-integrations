# Developer Guide: Integrating IBM DB2 with AI Frameworks

This guide shows developers how to integrate IBM DB2 into any AI framework using the IBM DB2 AI Connector utility library.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Integration Pattern](#integration-pattern)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Framework Examples](#framework-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

The IBM DB2 AI Connector provides a **framework-agnostic** core library that handles:
- Database connections
- SQL operations
- Vector search
- Error handling
- Connection pooling

Your job as a developer is to create a **thin wrapper** that translates your framework's API to the core library.

## Core Concepts

### 1. Configuration

All integrations start with `DB2Config`:

```python
from ibm_db2_ai import DB2Config

config = DB2Config(
    database="mydb",
    hostname="localhost",
    port=50000,
    username="db2user",
    password="password"
)
```

### 2. Connection Management

Use `DB2ConnectionManager` for safe connection handling:

```python
from ibm_db2_ai import DB2ConnectionManager

manager = DB2ConnectionManager(config)

# Context manager (recommended)
with manager as conn:
    # Use connection
    pass

# Manual management
conn = manager.connect()
# ... use connection ...
manager.close()
```

### 3. SQL Operations

Use `DB2SQLExecutor` for database operations:

```python
from ibm_db2_ai import DB2SQLExecutor

with manager as conn:
    executor = DB2SQLExecutor(conn)
    
    # SELECT
    results = executor.execute_query("SELECT * FROM table")
    
    # INSERT/UPDATE/DELETE
    affected = executor.execute_update("UPDATE table SET col = ?", params=(value,))
    
    # Batch operations
    executor.execute_many("INSERT INTO table VALUES (?, ?)", data_list)
```

### 4. Vector Operations

Use `DB2VectorStore` for similarity search:

```python
from ibm_db2_ai import DB2VectorStore

with manager as conn:
    vector_store = DB2VectorStore(
        connection=conn,
        table_name="embeddings",
        embedding_function=my_embedding_fn
    )
    
    # Add documents
    vector_store.add_texts(["text1", "text2"])
    
    # Search
    results = vector_store.search("query", k=5)
```

## Integration Pattern

Follow this pattern for any framework:

```
┌─────────────────────────────────────────┐
│  Your Framework (LangChain, AutoGen,    │
│  CrewAI, Haystack, n8n, etc.)           │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  Your Wrapper/Adapter                   │
│  - Translates framework API             │
│  - Handles framework-specific logic     │
│  - Maps to core library methods         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  IBM DB2 AI Connector (Core Library)    │
│  - DB2Config                            │
│  - DB2ConnectionManager                 │
│  - DB2SQLExecutor                       │
│  - DB2VectorStore                       │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  IBM DB2 Database                       │
└─────────────────────────────────────────┘
```

## Step-by-Step Guide

### Step 1: Install Dependencies

```bash
pip install ibm_db ibm_db_dbi
pip install -e /path/to/ibm-db2-ai-integrations/core
```

### Step 2: Create Base Connector Class

```python
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

class DB2Connector:
    """Base connector for any framework."""
    
    def __init__(self, config: DB2Config):
        self.config = config
        self.connection_manager = DB2ConnectionManager(config)
    
    def query(self, sql: str, params=None, max_rows=100):
        """Execute SELECT query."""
        with self.connection_manager as conn:
            executor = DB2SQLExecutor(conn)
            return executor.execute_query(sql, params, max_rows)
    
    def execute(self, sql: str, params=None):
        """Execute INSERT/UPDATE/DELETE."""
        with self.connection_manager as conn:
            executor = DB2SQLExecutor(conn)
            return executor.execute_update(sql, params)
    
    def close(self):
        """Close connection."""
        self.connection_manager.close()
```

### Step 3: Create Framework-Specific Wrapper

Adapt the base connector to your framework's API:

#### For LangChain Tools:

```python
from langchain.agents import Tool

def create_db2_tool(config: DB2Config):
    connector = DB2Connector(config)
    
    def query_db2(query: str) -> str:
        results = connector.query(query)
        return f"Results: {results}"
    
    return Tool(
        name="DB2Query",
        func=query_db2,
        description="Execute SQL on DB2"
    )
```

#### For AutoGen Agents:

```python
from autogen import ConversableAgent

def register_db2_functions(agent: ConversableAgent, config: DB2Config):
    connector = DB2Connector(config)
    
    def query_db2(query: str) -> dict:
        results = connector.query(query)
        return {"success": True, "results": results}
    
    agent.register_function(
        function_map={"query_db2": query_db2}
    )
```

#### For CrewAI Tools:

```python
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

class DB2QueryInput(BaseModel):
    query: str = Field(..., description="SQL query")

class DB2Tool(BaseTool):
    name: str = "DB2Query"
    description: str = "Execute SQL on DB2"
    args_schema: type[BaseModel] = DB2QueryInput
    
    def __init__(self, config: DB2Config):
        super().__init__()
        self.connector = DB2Connector(config)
    
    def _run(self, query: str) -> str:
        results = self.connector.query(query)
        return str(results)
```

#### For Haystack Document Stores:

```python
from haystack.document_stores import BaseDocumentStore
from haystack import Document

class DB2DocumentStore(BaseDocumentStore):
    def __init__(self, config: DB2Config):
        super().__init__()
        self.connector = DB2Connector(config)
    
    def write_documents(self, documents: List[Document]):
        # Use connector to store documents
        pass
    
    def get_all_documents(self):
        # Use connector to retrieve documents
        pass
```

### Step 4: Handle Framework-Specific Requirements

Each framework has unique requirements:

**LangChain:**
- Return strings or Documents
- Handle tool descriptions
- Support async if needed

**AutoGen:**
- Return dictionaries
- Register functions with agent
- Handle conversation context

**CrewAI:**
- Inherit from BaseTool
- Define Pydantic schemas
- Implement _run method

**Haystack:**
- Inherit from BaseDocumentStore
- Implement required methods
- Handle Document objects

**n8n:**
- Create TypeScript node
- Define credentials
- Handle JSON input/output

### Step 5: Add Error Handling

```python
def safe_query(connector, query):
    """Wrapper with error handling."""
    try:
        results = connector.query(query)
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }
```

### Step 6: Test Your Integration

```python
def test_integration():
    config = DB2Config(
        database="testdb",
        hostname="localhost",
        username="user",
        password="pass"
    )
    
    # Test basic query
    connector = DB2Connector(config)
    results = connector.query("SELECT 1 FROM SYSIBM.SYSDUMMY1")
    assert len(results) == 1
    
    # Test with your framework
    tool = create_your_framework_tool(config)
    result = tool.run("SELECT * FROM table")
    assert result is not None
```

## Framework Examples

### Complete LangChain Integration

```python
from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

# Configuration
config = DB2Config(database="mydb", hostname="localhost",
                   username="user", password="pass")

# Create tool
def query_db2(query: str) -> str:
    with DB2ConnectionManager(config) as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query(query)
        return f"Query returned {len(results)} rows: {results}"

db2_tool = Tool(
    name="DB2Query",
    func=query_db2,
    description="Execute SQL queries on DB2. Input: SQL query string."
)

# Use with agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    [db2_tool],
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Run
response = agent.run("How many users are in the database?")
```

### Complete AutoGen Integration

```python
from autogen import ConversableAgent, UserProxyAgent
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

# Configuration
config = DB2Config(database="mydb", hostname="localhost",
                   username="user", password="pass")
conn_manager = DB2ConnectionManager(config)

# Define functions
def query_db2(query: str) -> dict:
    with conn_manager as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query(query)
        return {"success": True, "results": results, "count": len(results)}

# Create agent
assistant = ConversableAgent(
    name="DB2Assistant",
    system_message="You can query DB2 database using query_db2 function.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "..."}]}
)

# Register function
assistant.register_function(
    function_map={"query_db2": query_db2}
)

# Create user proxy
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Query the users table and tell me how many records there are."
)
```

## Best Practices

### 1. Connection Management

✅ **DO:**
```python
# Use context managers
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    results = executor.execute_query(query)
```

❌ **DON'T:**
```python
# Manual management without cleanup
conn = manager.connect()
results = executor.execute_query(query)
# Forgot to close!
```

### 2. Error Handling

✅ **DO:**
```python
try:
    results = connector.query(sql)
    return {"success": True, "data": results}
except RuntimeError as e:
    logger.error(f"DB2 error: {e}")
    return {"success": False, "error": str(e)}
```

❌ **DON'T:**
```python
# Let exceptions propagate without handling
results = connector.query(sql)  # May crash your app
```

### 3. Configuration

✅ **DO:**
```python
# Use environment variables
config = DB2Config(
    database=os.getenv("DB2_DATABASE"),
    hostname=os.getenv("DB2_HOSTNAME"),
    username=os.getenv("DB2_USERNAME"),
    password=os.getenv("DB2_PASSWORD")
)
```

❌ **DON'T:**
```python
# Hardcode credentials
config = DB2Config(
    database="mydb",
    username="admin",
    password="password123"  # Security risk!
)
```

### 4. Resource Cleanup

✅ **DO:**
```python
connector = DB2Connector(config)
try:
    results = connector.query(sql)
finally:
    connector.close()
```

### 5. Parameterized Queries

✅ **DO:**
```python
# Use parameterized queries
results = executor.execute_query(
    "SELECT * FROM users WHERE age > ?",
    params=(25,)
)
```

❌ **DON'T:**
```python
# String concatenation (SQL injection risk!)
age = 25
results = executor.execute_query(
    f"SELECT * FROM users WHERE age > {age}"
)
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to DB2
```
RuntimeError: Failed to connect to DB2: [IBM][CLI Driver] SQL30081N
```

**Solution:**
1. Check hostname and port
2. Verify DB2 is running
3. Check firewall rules
4. Test with `db2 connect to database`

### Import Errors

**Problem:** Cannot import ibm_db2_ai
```
ModuleNotFoundError: No module named 'ibm_db2_ai'
```

**Solution:**
```bash
# Install in development mode
cd /path/to/ibm-db2-ai-integrations/core
pip install -e .
```

### Vector Search Issues

**Problem:** Vector dimension mismatch
```
ValueError: Embedding dimension mismatch: expected 768, got 384
```

**Solution:**
- Ensure embedding model matches table dimension
- Drop and recreate table with correct dimension
- Or use matching embedding model

### Performance Issues

**Problem:** Slow queries

**Solution:**
1. Add indexes to frequently queried columns
2. Use `max_rows` parameter to limit results
3. Use batch operations for multiple inserts
4. Consider connection pooling for high-traffic apps

## Next Steps

1. Review [examples/](../examples/) directory for complete examples
2. Check [API.md](API.md) for detailed API reference
3. See [README.md](../README.md) for quick start guide
4. Join discussions on GitHub for support

## Contributing

Found a bug or want to add support for a new framework? See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

**Need Help?**
- GitHub Issues: [Report a bug](https://github.com/yourusername/ibm-db2-ai-integrations/issues)
- Discussions: [Ask questions](https://github.com/yourusername/ibm-db2-ai-integrations/discussions)