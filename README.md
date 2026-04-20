# IBM DB2 AI Connector Utility Framework

A comprehensive, framework-agnostic utility library for integrating IBM DB2 databases with AI frameworks and applications. This SDK provides developers with ready-to-use components for SQL operations, vector search, and connection management.

## 🎯 Purpose

This utility framework enables developers to easily integrate IBM DB2 into **any AI framework** (LangChain, LangFlow, n8n, AutoGen, CrewAI, Haystack, etc.) without rewriting DB2 logic. It provides:

- ✅ **Framework-agnostic core library** - Works with any Python/TypeScript framework
- ✅ **Connection management** - Secure, pooled connections with context managers
- ✅ **SQL operations** - Execute queries, updates, batch operations
- ✅ **Vector store support** - Similarity search with DB2's vector capabilities
- ✅ **Type-safe** - Full type hints and validation
- ✅ **Production-ready** - Error handling, logging, and best practices

## 📦 Installation

```bash
# Install the core library
pip install ibm_db ibm_db_dbi

# Clone this repository
git clone https://github.com/yourusername/ibm-db2-ai-integrations.git
cd ibm-db2-ai-integrations

# Install in development mode
pip install -e ./core
```

## 🚀 Quick Start

### Basic SQL Operations

```python
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

# Configure connection
config = DB2Config(
    database="mydb",
    hostname="localhost",
    port=50000,
    username="db2user",
    password="password"
)

# Execute queries
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    # SELECT query
    results = executor.execute_query(
        "SELECT * FROM users WHERE age > ?",
        params=(25,),
        max_rows=100
    )
    print(f"Found {len(results)} users")
    
    # INSERT/UPDATE/DELETE
    affected = executor.execute_update(
        "UPDATE users SET status = ? WHERE id = ?",
        params=('active', 123)
    )
    print(f"Updated {affected} rows")
```

### Vector Search Operations

```python
from ibm_db2_ai import DB2VectorStore

# Initialize vector store
with DB2ConnectionManager(config) as conn:
    vector_store = DB2VectorStore(
        connection=conn,
        table_name="embeddings",
        embedding_function=my_embedding_model,
        distance_strategy="COSINE"
    )
    
    # Add documents
    vector_store.add_texts(
        texts=["AI is transforming industries", "Machine learning is powerful"],
        metadatas=[{"source": "doc1"}, {"source": "doc2"}]
    )
    
    # Search
    results = vector_store.search("artificial intelligence", k=5)
    for text, score, metadata in results:
        print(f"Score: {score:.4f} - {text}")
```

## 🔌 Integration Examples

### For LangChain

```python
from langchain.agents import Tool
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

config = DB2Config(database="mydb", hostname="localhost", 
                   username="user", password="pass")

def query_db2(query: str) -> str:
    with DB2ConnectionManager(config) as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query(query)
        return str(results)

db2_tool = Tool(
    name="DB2Query",
    func=query_db2,
    description="Execute SQL queries on DB2 database"
)

# Use with LangChain agent
from langchain.agents import initialize_agent
agent = initialize_agent([db2_tool], llm, agent="zero-shot-react-description")
```

### For AutoGen

```python
from autogen import ConversableAgent
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

config = DB2Config(database="mydb", hostname="localhost",
                   username="user", password="pass")
conn_manager = DB2ConnectionManager(config)

def query_db2(query: str) -> dict:
    with conn_manager as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query(query)
        return {"success": True, "results": results}

agent = ConversableAgent(name="DB2Assistant")
agent.register_function(function_map={"query_db2": query_db2})
```

### For CrewAI

```python
from crewai_tools import BaseTool
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

class DB2QueryTool(BaseTool):
    name: str = "DB2 Query"
    description: str = "Execute SQL queries on IBM DB2"
    
    def _run(self, query: str) -> str:
        config = DB2Config(database="mydb", hostname="localhost",
                          username="user", password="pass")
        with DB2ConnectionManager(config) as conn:
            executor = DB2SQLExecutor(conn)
            results = executor.execute_query(query)
            return f"Query returned {len(results)} rows: {results}"

# Use with CrewAI agent
from crewai import Agent
analyst = Agent(
    role='Data Analyst',
    tools=[DB2QueryTool()],
    goal='Analyze data from DB2'
)
```

### For n8n (Node.js/TypeScript)

```typescript
// Use Python bridge or native ibm_db module
import { PythonShell } from 'python-shell';

async function queryDB2(query: string): Promise<any> {
    const options = {
        mode: 'json',
        pythonPath: 'python3',
        scriptPath: './scripts',
        args: [query]
    };
    
    return PythonShell.run('db2_query.py', options);
}

// In your n8n node
const results = await queryDB2('SELECT * FROM users LIMIT 10');
```

### For Haystack

```python
from haystack import Document
from haystack.document_stores import BaseDocumentStore
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2VectorStore

class DB2DocumentStore(BaseDocumentStore):
    def __init__(self, db2_config: DB2Config):
        self.config = db2_config
        self.conn_manager = DB2ConnectionManager(db2_config)
    
    def write_documents(self, documents: List[Document]):
        with self.conn_manager as conn:
            vector_store = DB2VectorStore(conn, "haystack_docs", embedding_fn)
            texts = [doc.content for doc in documents]
            vector_store.add_texts(texts)
    
    def query_by_embedding(self, query_emb: List[float], top_k: int = 10):
        with self.conn_manager as conn:
            vector_store = DB2VectorStore(conn, "haystack_docs", embedding_fn)
            return vector_store.search(query_emb, k=top_k)
```

## 📚 Core Components

### 1. DB2Config
Configuration dataclass for DB2 connections.

```python
config = DB2Config(
    database="mydb",        # Required: Database name
    hostname="localhost",   # Required: Server hostname
    port=50000,            # Optional: Port (default: 50000)
    username="db2user",    # Required: Username
    password="password",   # Required: Password
    protocol="TCPIP",      # Optional: Protocol (default: TCPIP)
    ssl=False              # Optional: Enable SSL (default: False)
)
```

### 2. DB2ConnectionManager
Manages database connections with context manager support.

```python
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

### 3. DB2SQLExecutor
Execute SQL operations on DB2.

**Methods:**
- `execute_query(query, params, max_rows)` - Execute SELECT queries
- `execute_update(query, params)` - Execute INSERT/UPDATE/DELETE
- `execute_many(query, params_list)` - Batch operations
- `table_exists(table_name)` - Check if table exists
- `get_table_info(table_name)` - Get table structure

### 4. DB2VectorStore
Vector similarity search operations.

**Methods:**
- `add_texts(texts, metadatas, ids)` - Add documents
- `search(query, k, filter)` - Similarity search
- `delete(ids)` - Delete vectors
- `create_table()` - Create vector table
- `drop_table()` - Drop vector table

## 🛠️ Advanced Usage

### Connection Pooling

```python
# Reuse connection manager across operations
config = DB2Config(...)
manager = DB2ConnectionManager(config)

# Multiple operations with same connection
with manager as conn:
    executor = DB2SQLExecutor(conn)
    
    # Operation 1
    users = executor.execute_query("SELECT * FROM users")
    
    # Operation 2
    orders = executor.execute_query("SELECT * FROM orders")
    
    # Operation 3
    executor.execute_update("UPDATE users SET last_login = NOW()")
```

### Batch Operations

```python
# Insert multiple rows efficiently
data = [
    ('John', 30, 'john@example.com'),
    ('Jane', 25, 'jane@example.com'),
    ('Bob', 35, 'bob@example.com'),
]

with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    affected = executor.execute_many(
        "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
        data
    )
    print(f"Inserted {affected} rows")
```

### Error Handling

```python
from ibm_db2_ai import DB2ConnectionManager, DB2SQLExecutor

try:
    with DB2ConnectionManager(config) as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query("SELECT * FROM users")
except RuntimeError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Vector Search with Filters

```python
# Search with metadata filtering
results = vector_store.search(
    query="machine learning",
    k=10,
    filter={"category": ["AI", "ML"], "year": [2023, 2024]}
)

for text, score, metadata in results:
    print(f"{metadata['category']} - {score:.4f}: {text}")
```

## 📖 API Reference

See [docs/API.md](docs/API.md) for complete API documentation.

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=ibm_db2_ai tests/
```

## 🤝 Contributing

We welcome contributions! To integrate DB2 with a new framework:

1. Use the core `ibm_db2_ai` library
2. Create a thin wrapper for your framework
3. Add examples to `examples/` directory
4. Update documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [IBM DB2 Documentation](https://www.ibm.com/docs/en/db2/11.5)
- [IBM DB2 Vector Search](https://www.ibm.com/docs/en/db2/11.5?topic=features-vector-search)
- [Examples Directory](examples/)
- [API Documentation](docs/API.md)

## 💡 Use Cases

- **RAG Applications**: Store and search document embeddings
- **AI Agents**: Give agents database query capabilities
- **Data Analysis**: Execute complex SQL queries from AI workflows
- **Knowledge Bases**: Build vector-based knowledge retrieval systems
- **Multi-Agent Systems**: Share database access across multiple agents

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ibm-db2-ai-integrations/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ibm-db2-ai-integrations/discussions)
- **Email**: support@example.com

---

**Made with ❤️ for the AI community**