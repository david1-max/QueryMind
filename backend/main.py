from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import time
import os
import sys

# Import optimizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from optimizer import analyze_query

app = FastAPI(title="QueryMind SQL Optimizer API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "querymind_sandbox.db")

class QueryPayload(BaseModel):
    query: str

class ApplyPayload(BaseModel):
    query: str
    index_sql: str

# Initialize database schema and metadata table
def init_metadata_table():
    if not os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS querymind_optimizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        index_sql TEXT NOT NULL,
        time_before REAL NOT NULL,
        time_after REAL NOT NULL,
        speedup REAL NOT NULL,
        applied_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_metadata_table()

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "database_connected": os.path.exists(DB_PATH),
        "database_path": DB_PATH
    }

@app.post("/analyze")
def analyze(payload: QueryPayload):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = analyze_query(DB_PATH, payload.query)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/apply")
def apply_index(payload: ApplyPayload):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file not found")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Benchmark BEFORE
    start_time = time.perf_counter()
    try:
        cursor.execute(payload.query)
        cursor.fetchall()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Error executing query before index: {str(e)}")
    end_time = time.perf_counter()
    time_before_ms = (end_time - start_time) * 1000
    
    # 2. Get explain plan BEFORE
    cursor.execute(f"EXPLAIN QUERY PLAN {payload.query}")
    plan_before = [row[3] for row in cursor.fetchall()]
    
    # 3. Apply the index
    try:
        cursor.execute(payload.index_sql)
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Error creating index: {str(e)}")
        
    # 4. Benchmark AFTER
    start_time = time.perf_counter()
    try:
        cursor.execute(payload.query)
        cursor.fetchall()
    except Exception as e:
        # Rollback index on error to keep DB clean
        import re
        match = re.search(r'CREATE\s+INDEX\s+(\w+)', payload.index_sql, re.IGNORECASE)
        if match:
            cursor.execute(f"DROP INDEX IF EXISTS {match.group(1)}")
            conn.commit()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error executing query after index: {str(e)}")
    end_time = time.perf_counter()
    time_after_ms = (end_time - start_time) * 1000
    
    # 5. Get explain plan AFTER
    cursor.execute(f"EXPLAIN QUERY PLAN {payload.query}")
    plan_after = [row[3] for row in cursor.fetchall()]
    
    speedup = time_before_ms / time_after_ms if time_after_ms > 0 else 0
    applied_at = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the optimization in metadata table
    cursor.execute("""
    INSERT INTO querymind_optimizations (query_text, index_sql, time_before, time_after, speedup, applied_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (payload.query, payload.index_sql, time_before_ms, time_after_ms, speedup, applied_at))
    conn.commit()
    
    conn.close()
    
    return {
        "success": True,
        "time_before_ms": time_before_ms,
        "time_after_ms": time_after_ms,
        "speedup": f"{speedup:.2f}x",
        "plan_before": plan_before,
        "plan_after": plan_after
    }

@app.get("/history")
def get_history():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM querymind_optimizations ORDER BY id DESC")
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history
