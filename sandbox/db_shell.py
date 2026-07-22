import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "querymind_sandbox.db")

def run_shell():
    print("=" * 60)
    print("QueryMind Interactive Python DB Shell (SQLite)")
    print(f"Connected to: {DB_PATH}")
    print("Type '.exit' to leave. Type SQL queries ending with ';'")
    print("Dot-commands: .tables, .schema <table_name>")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}. Run seeder.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    buffer = ""
    while True:
        try:
            prompt = "sqlite> " if not buffer else "   ...> "
            line = input(prompt)
            if not line.strip():
                continue
            if line.strip().lower() in [".exit", ".quit", "exit", "quit"]:
                break
            if line.strip().startswith("."):
                cmd = line.strip().lower()
                if cmd == ".tables":
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    print("Tables:")
                    for row in tables:
                        print(f"  - {row[0]}")
                elif cmd.startswith(".schema"):
                    parts = cmd.split()
                    if len(parts) > 1:
                        table = parts[1]
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                        row = cursor.fetchone()
                        if row:
                            print(row[0])
                        else:
                            print(f"Table '{table}' not found.")
                    else:
                        print("Usage: .schema <table_name>")
                else:
                    print(f"Unknown dot-command: {line}")
                continue
            
            buffer += " " + line
            if buffer.strip().endswith(";"):
                query = buffer.strip()
                buffer = ""
                start_time = time.perf_counter()
                try:
                    cursor.execute(query)
                    # If query returns results, print them
                    if cursor.description:
                        cols = [description[0] for description in cursor.description]
                        print(" | ".join(cols))
                        print("-" * 60)
                        rows = cursor.fetchall()
                        for row in rows:
                            print(" | ".join(str(val) for val in row))
                        print(f"({len(rows)} rows returned in {(time.perf_counter() - start_time)*1000:.2f} ms)")
                    else:
                        conn.commit()
                        print(f"Query executed successfully in {(time.perf_counter() - start_time)*1000:.2f} ms.")
                except Exception as e:
                    print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = ""
        except EOFError:
            break
            
    conn.close()

if __name__ == "__main__":
    run_shell()
