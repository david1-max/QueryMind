# 🧠 QueryMind: AI-Powered SQL Query Optimizer

QueryMind is a developer utility designed to monitor, analyze, and optimize SQL database performance. It hooks into your database, executes `EXPLAIN QUERY PLAN` on queries, isolates unoptimized table scan bottlenecks, recommends appropriate indexing, and benchmarks the latency improvement side-by-side.

---

## 📊 Live Benchmark Metrics

When tested against a sandbox database seeded with **300,000 mock rows** (50,000 users, 250,000 orders), QueryMind achieved the following query performance speedups:

| Query Scenario | Scan Pattern (Before) | Scan Pattern (After) | Speedup Ratio |
| :--- | :--- | :--- | :--- |
| **Single User Lookup by Email** | `SCAN users` | `SEARCH users USING INDEX idx_users_email (email=?)` | **57.30x Speedup** |
| **User & Orders Join** | `SCAN orders` | `SEARCH orders USING INDEX idx_orders_user_id (user_id=?)` | **36.58x Speedup** |
| **Filter & Sort Orders** | `SCAN orders` | `SEARCH orders USING INDEX idx_orders_status (status=?)` | **1.12x Speedup** |

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, Python, Uvicorn, SQLite
* **Frontend:** React, Vite, Custom HSL Styling (Dark mode, glassmorphic layout), Lucide Icons
* **Database Sandbox:** SQLite (pre-seeded with 300,000 rows for realistic latency metrics)

---

## 🚀 Features

1. **Plan Parser:** Automated scanning of SQLite execution plan instructions. Detects `SCAN` steps that indicate a full-table scan.
2. **Correlation Engine:** Queries schema metadata using `PRAGMA table_info` and matches sequential scans to target columns in `WHERE`, `JOIN ON`, or `ORDER BY` clauses.
3. **One-Click Optimization:** Automatically compiles and runs `CREATE INDEX` queries directly from the UI.
4. **Interactive Dashboard:** Modern dark-mode React interface showing template queries, side-by-side plan comparisons, and a visual benchmark bar chart.
5. **Optimization Log:** Tracks all historical query speedups in a persistent metadata table (`querymind_optimizations`).

---

## 🏃 Getting Started

### 1. Pre-requisites
Ensure you have **Python 3.10+** and **Node.js 16+** installed.

### 2. Backend Setup
1. Navigate to the backend directory and install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Seed the sandbox database with 300,000 mock rows:
   ```bash
   python sandbox/seeder.py
   ```
3. Launch the FastAPI server:
   ```bash
   python -m uvicorn backend.main:app --port 8000 --host 127.0.0.1
   ```
   The interactive API docs will be live at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
1. Navigate to the frontend directory and install NPM packages:
   ```bash
   npm install
   ```
2. Run the Vite development server:
   ```bash
   npm run dev -- --port 3000 --host 127.0.0.1
   ```
3. Open your browser and navigate to **`http://127.0.0.1:3000/`** to view the dashboard!

---

## 🧪 Running Standalone Tests
You can also run a headless benchmark comparison in your terminal using:
```bash
python sandbox/benchmark_runner.py
```
This runs the test queries, registers suggestions, applies indexes, measures speedup, and drops the temporary indexes afterwards to reset the database.
