import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "querymind_sandbox.db")

def seed_db():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # Create tables (only primary key indexes created automatically)
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        ordered_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    print("Tables created.")

    # Generate user data
    first_names = ["Rahul", "Amit", "Priya", "Neha", "Divyanshu", "Sanjay", "Anjali", "Vikram", "Rohan", "Sneha", "Karan", "Pooja", "Arjun", "Aditi", "Vijay", "Deepa"]
    last_names = ["Yadav", "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Joshi", "Patel", "Mehta", "Choudhary", "Reddy", "Nair"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "jklu.edu.in", "hotmail.com"]
    statuses = ["PENDING", "COMPLETED", "SHIPPED", "CANCELLED", "REFUNDED"]

    print("Generating 50,000 users...")
    users = []
    base_date = datetime(2025, 1, 1)
    for i in range(1, 50001):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@{random.choice(domains)}"
        created_at = (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
        users.append((name, email, created_at))
        
    cursor.executemany("INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)", users)
    conn.commit()
    print("Users inserted.")

    print("Generating 250,000 orders...")
    orders = []
    for i in range(1, 250001):
        user_id = random.randint(1, 50000)
        amount = round(random.uniform(10.0, 5000.0), 2)
        status = random.choice(statuses)
        ordered_at = (base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")
        orders.append((user_id, amount, status, ordered_at))

    chunk_size = 50000
    for j in range(0, len(orders), chunk_size):
        cursor.executemany("INSERT INTO orders (user_id, amount, status, ordered_at) VALUES (?, ?, ?, ?)", orders[j:j+chunk_size])
        conn.commit()
        
    print("Orders inserted successfully.")
    
    # Print table sizes
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"Total Users: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM orders")
    print(f"Total Orders: {cursor.fetchone()[0]}")
    
    conn.close()

if __name__ == "__main__":
    seed_db()
