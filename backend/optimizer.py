import sqlite3
import re
import os

def get_table_columns(conn, table_name):
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]
    except Exception:
        return []

def analyze_query(db_path, query):
    if not os.path.exists(db_path):
        return {"error": f"Database file not found at: {db_path}"}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Run EXPLAIN QUERY PLAN
    try:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan_rows = cursor.fetchall()
    except Exception as e:
        conn.close()
        return {"error": f"Invalid query: {str(e)}"}
        
    scanned_tables = []
    for row in plan_rows:
        detail = row[3]
        # Match 'SCAN' or 'SCAN TABLE' followed by table name
        match = re.search(r'\bSCAN\s+(?:TABLE\s+)?(\w+)', detail, re.IGNORECASE)
        if match:
            scanned_tables.append(match.group(1))
            
    recommendations = []
    
    # Normalize query for parsing: convert newlines to spaces, reduce spaces
    normalized_query = " " + re.sub(r'\s+', ' ', query) + " "
    
    # Split query into clauses (case-insensitive split)
    clauses = {
        "where": "",
        "join_on": "",
        "order_by": "",
        "group_by": ""
    }
    
    # Regex to find clauses
    where_match = re.search(r'\bWHERE\b(.*?)(\bORDER\s+BY\b|\bGROUP\s+BY\b|\bLIMIT\b|$)', normalized_query, re.IGNORECASE)
    if where_match:
        clauses["where"] = where_match.group(1)
        
    on_matches = re.findall(r'\bON\b(.*?)(?:\bJOIN\b|\bWHERE\b|\bORDER\s+BY\b|\bGROUP\s+BY\b|\bLIMIT\b|$)', normalized_query, re.IGNORECASE)
    if on_matches:
        clauses["join_on"] = " ".join(on_matches)
        
    order_match = re.search(r'\bORDER\s+BY\b(.*?)(\bLIMIT\b|$)', normalized_query, re.IGNORECASE)
    if order_match:
        clauses["order_by"] = order_match.group(1)
        
    group_match = re.search(r'\bGROUP\s+BY\b(.*?)(\bORDER\s+BY\b|\bLIMIT\b|$)', normalized_query, re.IGNORECASE)
    if group_match:
        clauses["group_by"] = group_match.group(1)

    for table in scanned_tables:
        columns = get_table_columns(conn, table)
        
        for col in columns:
            col_pattern = rf'\b(?:{table}\.)?{col}\b'
            
            # 1. Look in WHERE clause
            if re.search(col_pattern, clauses["where"], re.IGNORECASE):
                recommendations.append({
                    "table": table,
                    "column": col,
                    "reason": f"Column '{col}' is used in WHERE clause filtering during a full table scan.",
                    "sql": f"CREATE INDEX idx_{table}_{col} ON {table}({col});"
                })
                
            # 2. Look in JOIN ON clause
            elif re.search(col_pattern, clauses["join_on"], re.IGNORECASE):
                recommendations.append({
                    "table": table,
                    "column": col,
                    "reason": f"Column '{col}' is used as a JOIN condition key during a full table scan.",
                    "sql": f"CREATE INDEX idx_{table}_{col} ON {table}({col});"
                })
                
            # 3. Look in ORDER BY clause
            elif re.search(col_pattern, clauses["order_by"], re.IGNORECASE):
                recommendations.append({
                    "table": table,
                    "column": col,
                    "reason": f"Column '{col}' is used in ORDER BY sorting during a full table scan.",
                    "sql": f"CREATE INDEX idx_{table}_{col} ON {table}({col});"
                })
                
    conn.close()
    
    # De-duplicate recommendations by index name / SQL
    seen_sql = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec["sql"] not in seen_sql:
            seen_sql.add(rec["sql"])
            unique_recommendations.append(rec)

    return {
        "scanned_tables": list(set(scanned_tables)),
        "recommendations": unique_recommendations,
        "explain_plan": [row[3] for row in plan_rows]
    }

if __name__ == "__main__":
    # Test execution
    db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "querymind_sandbox.db")
    test_query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.email = 'test'"
    print("Testing Optimizer with Query:")
    print(test_query)
    print("\nResult:")
    import json
    print(json.dumps(analyze_query(db, test_query), indent=2))
