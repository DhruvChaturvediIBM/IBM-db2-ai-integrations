# Quick Start Guide: IBM DB2 AI Connector

Get started with IBM DB2 AI Connector in 5 minutes!

## Installation

```bash
# Install IBM DB2 drivers
pip install ibm_db ibm_db_dbi

# Clone the repository
git clone https://github.com/yourusername/ibm-db2-ai-integrations.git
cd ibm-db2-ai-integrations

# Install the core library
pip install -e ./core
```

## Basic Usage

### 1. Configure Connection

```python
from ibm_db2_ai import DB2Config

config = DB2Config(
    database="SAMPLE",      # Your database name
    hostname="localhost",   # Your DB2 server
    port=50000,            # Default DB2 port
    username="db2inst1",   # Your username
    password="password"    # Your password
)
```

### 2. Execute SQL Query

```python
from ibm_db2_ai import DB2ConnectionManager, DB2SQLExecutor

# Query the database
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    # Simple SELECT
    results = executor.execute_query("SELECT * FROM EMPLOYEE LIMIT 10")
    
    print(f"Found {len(results)} employees")
    for row in results:
        print(row)
```

### 3. Insert Data

```python
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    # Insert a record
    affected = executor.execute_update(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        params=('John Doe', 'john@example.com')
    )
    
    print(f"Inserted {affected} row(s)")
```

### 4. Vector Search (Optional)

```python
from ibm_db2_ai import DB2VectorStore

# Assuming you have an embedding function
def my_embedding_function(text):
    # Your embedding logic here
    return [0.1, 0.2, 0.3, ...]  # Return embedding vector

with DB2ConnectionManager(config) as conn:
    vector_store = DB2VectorStore(
        connection=conn,
        table_name="documents",
        embedding_function=my_embedding_function
    )
    
    # Add documents
    vector_store.add_texts([
        "AI is transforming industries",
        "Machine learning powers modern applications"
    ])
    
    # Search
    results = vector_store.search("artificial intelligence", k=5)
    for text, score, metadata in results:
        print(f"Score: {score:.4f} - {text}")
```

## Integration with AI Frameworks

### LangChain

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
    description="Execute SQL queries on DB2"
)

# Use with your LangChain agent
```

### AutoGen

```python
from autogen import ConversableAgent
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

config = DB2Config(database="mydb", hostname="localhost",
                   username="user", password="pass")

def query_db2(query: str) -> dict:
    with DB2ConnectionManager(config) as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query(query)
        return {"success": True, "results": results}

agent = ConversableAgent(name="DB2Assistant")
agent.register_function(function_map={"query_db2": query_db2})
```

### CrewAI

```python
from crewai_tools import BaseTool
from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor

class DB2Tool(BaseTool):
    name: str = "DB2Query"
    description: str = "Execute SQL on DB2"
    
    def _run(self, query: str) -> str:
        config = DB2Config(database="mydb", hostname="localhost",
                          username="user", password="pass")
        with DB2ConnectionManager(config) as conn:
            executor = DB2SQLExecutor(conn)
            results = executor.execute_query(query)
            return str(results)

# Use with CrewAI agent
```

## Environment Variables (Recommended)

Create a `.env` file:

```bash
DB2_DATABASE=SAMPLE
DB2_HOSTNAME=localhost
DB2_PORT=50000
DB2_USERNAME=db2inst1
DB2_PASSWORD=your_password
```

Use in your code:

```python
import os
from dotenv import load_dotenv
from ibm_db2_ai import DB2Config

load_dotenv()

config = DB2Config(
    database=os.getenv("DB2_DATABASE"),
    hostname=os.getenv("DB2_HOSTNAME"),
    port=int(os.getenv("DB2_PORT", "50000")),
    username=os.getenv("DB2_USERNAME"),
    password=os.getenv("DB2_PASSWORD")
)
```

## Common Operations

### Check if Table Exists

```python
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    if executor.table_exists("USERS"):
        print("Table exists!")
    else:
        print("Table does not exist")
```

### Get Table Structure

```python
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    columns = executor.get_table_info("EMPLOYEE")
    for col in columns:
        print(f"{col['COLUMN_NAME']}: {col['DATA_TYPE']}")
```

### Batch Insert

```python
with DB2ConnectionManager(config) as conn:
    executor = DB2SQLExecutor(conn)
    
    data = [
        ('Alice', 'alice@example.com', 25),
        ('Bob', 'bob@example.com', 30),
        ('Charlie', 'charlie@example.com', 35),
    ]
    
    affected = executor.execute_many(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        data
    )
    
    print(f"Inserted {affected} rows")
```

## Error Handling

```python
from ibm_db2_ai import DB2ConnectionManager, DB2SQLExecutor

try:
    with DB2ConnectionManager(config) as conn:
        executor = DB2SQLExecutor(conn)
        results = executor.execute_query("SELECT * FROM users")
        print(f"Success! Got {len(results)} rows")
        
except RuntimeError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

- 📖 Read the [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed integration instructions
- 🔍 Check [examples/](examples/) for complete working examples
- 📚 Review [API Documentation](docs/API.md) for all available methods
- 💡 See [README.md](README.md) for more use cases

## Troubleshooting

### Cannot connect to DB2

```bash
# Test DB2 connection
db2 connect to SAMPLE user db2inst1

# Check if DB2 is running
db2 list active databases
```

### Module not found

```bash
# Reinstall the library
cd /path/to/ibm-db2-ai-integrations/core
pip install -e .
```

### Import errors

```bash
# Install IBM DB2 drivers
pip install ibm_db ibm_db_dbi
```

## Support

- 🐛 [Report Issues](https://github.com/yourusername/ibm-db2-ai-integrations/issues)
- 💬 [Discussions](https://github.com/yourusername/ibm-db2-ai-integrations/discussions)
- 📧 Email: support@example.com

---

**Ready to integrate?** Check out the [integration template](examples/integration_template.py) for your framework!