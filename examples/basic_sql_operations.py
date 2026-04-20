"""
Example: Basic SQL Operations with IBM DB2 AI Connector

This example demonstrates how to use the IBM DB2 AI Connector for
basic SQL operations including SELECT, INSERT, UPDATE, and DELETE.
"""

import sys
import os

# Add core module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../core/src'))

from ibm_db2_ai import DB2Config, DB2ConnectionManager, DB2SQLExecutor


def main():
    """Demonstrate basic SQL operations."""
    
    # Step 1: Configure DB2 connection
    print("=" * 60)
    print("IBM DB2 AI Connector - Basic SQL Operations Example")
    print("=" * 60)
    
    config = DB2Config(
        database="SAMPLE",      # Replace with your database name
        hostname="localhost",   # Replace with your hostname
        port=50000,
        username="db2inst1",    # Replace with your username
        password="password"     # Replace with your password
    )
    
    print(f"\n✓ Configuration created for database: {config.database}")
    
    # Step 2: Create connection manager
    manager = DB2ConnectionManager(config)
    print(f"✓ Connection manager initialized")
    
    try:
        # Step 3: Execute SELECT query
        print("\n" + "-" * 60)
        print("Example 1: SELECT Query")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            # Simple SELECT
            results = executor.execute_query(
                "SELECT * FROM EMPLOYEE FETCH FIRST 5 ROWS ONLY"
            )
            
            print(f"✓ Query executed successfully")
            print(f"✓ Retrieved {len(results)} rows")
            
            if results:
                print("\nFirst row:")
                for key, value in results[0].items():
                    print(f"  {key}: {value}")
        
        # Step 4: Parameterized query
        print("\n" + "-" * 60)
        print("Example 2: Parameterized Query")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            results = executor.execute_query(
                "SELECT EMPNO, FIRSTNME, LASTNAME FROM EMPLOYEE WHERE WORKDEPT = ?",
                params=('A00',),
                max_rows=10
            )
            
            print(f"✓ Parameterized query executed")
            print(f"✓ Found {len(results)} employees in department A00")
        
        # Step 5: INSERT operation
        print("\n" + "-" * 60)
        print("Example 3: INSERT Operation")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            # Check if table exists
            if not executor.table_exists("TEST_USERS"):
                print("Creating TEST_USERS table...")
                executor.execute_update("""
                    CREATE TABLE TEST_USERS (
                        id INTEGER NOT NULL PRIMARY KEY,
                        name VARCHAR(100),
                        email VARCHAR(100),
                        age INTEGER
                    )
                """)
                print("✓ Table created")
            
            # Insert a record
            affected = executor.execute_update(
                "INSERT INTO TEST_USERS (id, name, email, age) VALUES (?, ?, ?, ?)",
                params=(1, 'John Doe', 'john@example.com', 30)
            )
            
            print(f"✓ Inserted {affected} row(s)")
        
        # Step 6: Batch INSERT
        print("\n" + "-" * 60)
        print("Example 4: Batch INSERT")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            # Prepare batch data
            users = [
                (2, 'Jane Smith', 'jane@example.com', 25),
                (3, 'Bob Johnson', 'bob@example.com', 35),
                (4, 'Alice Williams', 'alice@example.com', 28),
            ]
            
            affected = executor.execute_many(
                "INSERT INTO TEST_USERS (id, name, email, age) VALUES (?, ?, ?, ?)",
                users
            )
            
            print(f"✓ Batch insert completed: {affected} rows affected")
        
        # Step 7: UPDATE operation
        print("\n" + "-" * 60)
        print("Example 5: UPDATE Operation")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            affected = executor.execute_update(
                "UPDATE TEST_USERS SET age = ? WHERE name = ?",
                params=(31, 'John Doe')
            )
            
            print(f"✓ Updated {affected} row(s)")
        
        # Step 8: Verify UPDATE
        print("\n" + "-" * 60)
        print("Example 6: Verify Data")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            results = executor.execute_query(
                "SELECT * FROM TEST_USERS ORDER BY id"
            )
            
            print(f"✓ Current data in TEST_USERS:")
            for row in results:
                print(f"  ID: {row['ID']}, Name: {row['NAME']}, "
                      f"Email: {row['EMAIL']}, Age: {row['AGE']}")
        
        # Step 9: Get table information
        print("\n" + "-" * 60)
        print("Example 7: Table Information")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            columns = executor.get_table_info("TEST_USERS")
            
            print(f"✓ Table structure for TEST_USERS:")
            for col in columns:
                print(f"  {col['COLUMN_NAME']}: {col['DATA_TYPE']} "
                      f"(Length: {col['LENGTH']}, Nullable: {col['NULLABLE']})")
        
        # Step 10: DELETE operation
        print("\n" + "-" * 60)
        print("Example 8: DELETE Operation")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            affected = executor.execute_update(
                "DELETE FROM TEST_USERS WHERE age < ?",
                params=(30,)
            )
            
            print(f"✓ Deleted {affected} row(s)")
        
        # Step 11: Cleanup
        print("\n" + "-" * 60)
        print("Cleanup")
        print("-" * 60)
        
        with manager as conn:
            executor = DB2SQLExecutor(conn)
            
            # Drop test table
            executor.execute_update("DROP TABLE TEST_USERS")
            print("✓ Test table dropped")
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        manager.close()
        print("\n✓ Connection closed")


if __name__ == "__main__":
    main()

# Made with Bob
