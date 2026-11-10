from typing import Optional
"""Agent 3: SQL Validator - safety + syntax."""
import re, sqlite3
from config import SCHEMA

BLOCKED = ["INSERT","UPDATE","DELETE","DROP","ALTER","CREATE","TRUNCATE","REPLACE","GRANT","REVOKE","PRAGMA","ATTACH","DETACH","VACUUM","CALL","EXEC"]
ALLOWED_TABLES = set(SCHEMA.keys())

class ValidationError(ValueError):
    pass

def validate_sql(sql: str, params: Optional[list] = None):
    s = sql.strip()
    if not s:
        raise ValidationError("Empty SQL")
    # No multiple statements: allow single trailing ;
    core = s.rstrip(";")
    if ";" in core:
        raise ValidationError("Multiple statements not allowed")
    if "--" in s or "/*" in s:
        raise ValidationError("SQL comments not allowed")
    upper = s.upper()
    # Must start with SELECT or WITH
    if not (upper.lstrip().startswith("SELECT") or upper.lstrip().startswith("WITH")):
        raise ValidationError("Only SELECT queries allowed")
    for kw in BLOCKED:
        if re.search(rf"\b{kw}\b", upper):
            raise ValidationError(f"Blocked keyword: {kw}")
    # Syntax check via EXPLAIN (no execution)
    con = sqlite3.connect(":memory:")
    con.executescript("CREATE TABLE products(id INTEGER, name TEXT, category TEXT, price REAL, stock INTEGER); CREATE TABLE customers(id INTEGER, name TEXT, city TEXT, email TEXT); CREATE TABLE orders(id INTEGER, customer_id INTEGER, product_id INTEGER, quantity INTEGER, total_amount REAL, order_date TEXT);")
    try:
        con.execute(f"EXPLAIN {s}", params or [])
    except sqlite3.Error as e:
        raise ValidationError(f"Syntax error: {e}")
    finally:
        con.close()
    # LIMIT enforcement hint
    if "LIMIT" not in upper:
        raise ValidationError("Query must include LIMIT (use LIMIT ?)")
    return True
