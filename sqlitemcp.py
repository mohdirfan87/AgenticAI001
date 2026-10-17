import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")
# from mcp.server import MCPServer # Simpler import from the root module

# mcp = MCPServer("Math") # Exposes your core server interface

# 2. Initialize using MCPServer instead of FastMCP


# from mcp.server.fastmcp import FastMCP

conn = sqlite3.connect("shop3.db", check_same_thread = False)

# mcp = FastMCP("sale-mcp-server")
# mcp = MCPServer("sale-mcp-server")

conn.execute("DROP TABLE IF EXISTS users")
conn.execute("DROP TABLE IF EXISTS orders")
# ... followed by your CREATE TABLE statement blocks

# Create users table
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    signup_date DATE
)
''')

# Create orders table
conn.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    status TEXT,
    order_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Insert users
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'Alice', 'alice@example.com', '2024-01-10')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'Bob', 'bob@example.com', '2024-03-15')")
conn.execute("INSERT OR IGNORE INTO users VALUES (3, 'Charlie', 'charlie@example.com', '2024-03-22')")
conn.execute("INSERT OR IGNORE INTO users VALUES (4, 'Diana', 'diana@example.com', '2024-04-05')")
conn.execute("INSERT OR IGNORE INTO users VALUES (5, 'Eve', 'eve@example.com', '2024-04-25')")
conn.execute("INSERT OR IGNORE INTO users VALUES (6, 'Frank', 'frank@example.com', '2024-05-15')")
conn.execute("INSERT OR IGNORE INTO users VALUES (7, 'Grace', 'grace@example.com', '2024-05-18')")
conn.execute("INSERT OR IGNORE INTO users VALUES (8, 'Henry', 'henry@example.com', '2024-05-20')")
conn.execute("INSERT OR IGNORE INTO users VALUES (9, 'Ivy', 'ivy@example.com', '2024-06-01')")
conn.execute("INSERT OR IGNORE INTO users VALUES (10, 'Jack', 'jack@example.com', '2024-06-05')")
conn.execute("INSERT OR IGNORE INTO users VALUES (11, 'Kiran', 'kiran@example.com', '2024-06-03')")
conn.execute("INSERT OR IGNORE INTO users VALUES (12, 'Lata', 'lata@example.com', '2024-06-04')")
conn.execute("INSERT OR IGNORE INTO users VALUES (13, 'Manoj', 'manoj@example.com', '2024-06-06')")

# Insert orders
conn.execute("INSERT OR IGNORE INTO orders VALUES (1, 1, 250.00, 'completed', '2024-03-10')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (2, 2, 100.00, 'pending', '2024-03-16')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (3, 3, 320.00, 'completed', '2024-03-24')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (4, 4, 180.00, 'completed', '2024-05-01')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (5, 5, 210.00, 'completed', '2024-05-02')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (6, 1, 180.00, 'completed', '2024-03-18')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (7, 2, 120.00, 'completed', '2024-03-20')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (8, 1, 300.00, 'completed', '2024-04-01')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (9, 3, 80.00, 'cancelled', '2024-04-10')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (10, 4, 250.00, 'pending', '2024-05-05')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (11, 6, 400.00, 'completed', '2024-05-20')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (12, 7, 320.00, 'completed', '2024-05-22')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (13, 8, 150.00, 'pending', '2024-05-25')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (14, 9, 220.00, 'completed', '2024-06-02')")
conn.execute("INSERT OR IGNORE INTO orders VALUES (15, 10, 500.00, 'completed', '2024-06-06')")


# print("INSERT completed")

import sys

# Ensure this pattern is used anywhere you print updates:
print("INSERT completed", file=sys.stderr)

conn.commit()


@mcp.tool()
def get_schema() -> str:
    """Returns table schemas from the SQLite database."""
    schema = ""
    
    # Open the connection safely for this context block
  
    for table in ["users", "orders"]:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        if not rows:
            continue
        cols = ",".join([f"{r[1]} {r[2]}" for r in rows])
        schema += f"{table}({cols})\n"
            
    return schema.strip() if schema else "No tables found."

@mcp.tool()
def execute_sql(query: str) -> str:
    """Executes an SQL query on the database and returns the result."""
    try:
        # Open the connection safely for this block
        cursor = conn.execute(query)
        
        # If it's a structural/write operation (INSERT, UPDATE, DELETE)
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
        
        # If it's a read operation (SELECT)
        result = cursor.fetchall()
        return str(result)
            
    except Exception as e:
        return f"Error: {str(e)}"



if __name__ == "__main__":
    mcp.run(transport="stdio")