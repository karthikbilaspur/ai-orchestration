from typing import Optional
"""Agent 4: Database Agent - read-only execution."""
import sqlite3
from config import DB_PATH, MAX_ROWS, QUERY_TIMEOUT

def execute_readonly(sql: str, params: Optional[list] = None, db_path=DB_PATH):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=QUERY_TIMEOUT)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql, params or [])
        rows = cur.fetchmany(MAX_ROWS)
        cols = [d[0] for d in cur.description] if cur.description else []
        return {"columns": cols, "rows": [dict(r) for r in rows], "row_count": len(rows)}
    finally:
        con.close()
