import sqlite3
import time
import os
import sys
import re

# Import optimizer from backend
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from backend.optimizer import analyze_query

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "querymind_sandbox.db")

BENCHMARK_QUERIES = [
    {
        "name": "Single user lookup by email",
        "query": "SELECT * FROM users WHERE email = 'neha.yadav100@gmail.com'"
    },
    {
        "name": "Join users and orders on user_id",
        "query": "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.name = 'Divyanshu Yadav'"
    },
    {
        "name": "Sort orders by date for pending orders",
        "query": "SELECT * FROM orders WHERE status = 'PENDING' ORDER BY ordered_at DESC LIMIT 10"
    }
]

def run_benchmarks():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run seeder.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("STARTING QUERYMIND SQL BENCHMARK RUNNER")
    print("=" * 70)

    results = []
    created_indexes = []

    for item in BENCHMARK_QUERIES:
        name = item["name"]
        query = item["query"]
        print(f"\nRunning Scenario: {name}...")
        print(f"SQL: {query}")

        # Explain Plan BEFORE
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan_before = [row[3] for row in cursor.fetchall()]
        print(f"Explain Plan Before: {plan_before}")

        # Measure Time BEFORE
        start_time = time.perf_counter()
        cursor.execute(query)
        cursor.fetchall()
        end_time = time.perf_counter()
        time_before_ms = (end_time - start_time) * 1000
        print(f"Execution Time Before: {time_before_ms:.2f} ms")

        # Get recommendations
        analysis = analyze_query(DB_PATH, query)
        recs = analysis.get("recommendations", [])
        
        applied_indexes = []
        if recs:
            print(f"Found {len(recs)} index recommendation(s):")
            for rec in recs:
                sql = rec["sql"]
                reason = rec["reason"]
                print(f"  [+] Suggestion: {sql}")
                print(f"      Reason: {reason}")
                
                # Apply index
                try:
                    cursor.execute(sql)
                    conn.commit()
                    applied_indexes.append(sql)
                    created_indexes.append(sql)
                except sqlite3.OperationalError as e:
                    print(f"     Error applying index: {str(e)}")
        else:
            print("  No optimization recommendations found.")

        # Explain Plan AFTER
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan_after = [row[3] for row in cursor.fetchall()]
        print(f"Explain Plan After: {plan_after}")

        # Measure Time AFTER
        start_time = time.perf_counter()
        cursor.execute(query)
        cursor.fetchall()
        end_time = time.perf_counter()
        time_after_ms = (end_time - start_time) * 1000
        print(f"Execution Time After: {time_after_ms:.2f} ms")

        speedup = time_before_ms / time_after_ms if time_after_ms > 0 else 0
        results.append({
            "name": name,
            "time_before": time_before_ms,
            "time_after": time_after_ms,
            "speedup": speedup,
            "applied": ", ".join(applied_indexes)
        })

    # Clean up applied indexes to reset the database sandbox
    print("\n" + "=" * 70)
    print("CLEANING UP APPLIED INDEXES TO RESET SANDBOX")
    print("=" * 70)
    for index_sql in created_indexes:
        match = re.search(r'CREATE\s+INDEX\s+(\w+)', index_sql, re.IGNORECASE)
        if match:
            idx_name = match.group(1)
            print(f"Dropping index: {idx_name}")
            cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")
    conn.commit()
    conn.close()

    # Print final benchmarking table
    print("\n" + "=" * 70)
    print("BENCHMARK COMPARISON RESULTS")
    print("=" * 70)
    print(f"{'Query Scenario':<38} | {'Before (ms)':<12} | {'After (ms)':<12} | {'Speedup':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<38} | {r['time_before']:11.2f} | {r['time_after']:11.2f} | {r['speedup']:.2f}x")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmarks()
