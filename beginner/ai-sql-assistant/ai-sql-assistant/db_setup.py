"""Seed SQLite DB with sample e-commerce data."""
import sqlite3, random
from pathlib import Path
from config import DB_PATH

PRODUCTS = [
    (1, "Wireless Mouse", "Electronics", 799, 120),
    (2, "Mechanical Keyboard", "Electronics", 2999, 60),
    (3, "Noise Cancelling Headphones", "Electronics", 4999, 45),
    (4, "Cotton T-Shirt", "Apparel", 499, 300),
    (5, "Running Shoes", "Apparel", 2499, 80),
    (6, "Coffee Mug", "Home", 299, 200),
    (7, "Desk Lamp", "Home", 1299, 70),
    (8, "Smart Watch", "Electronics", 8999, 30),
]
CUSTOMERS = [
    (1, "Aarav Sharma", "Bangalore", "aarav@example.com"),
    (2, "Priya Nair", "Mumbai", "priya@example.com"),
    (3, "Rohan Gupta", "Delhi", "rohan@example.com"),
    (4, "Sneha Iyer", "Chennai", "sneha@example.com"),
    (5, "Vikram Rao", "Hyderabad", "vikram@example.com"),
]

def setup(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER);
    CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, city TEXT, email TEXT);
    CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, product_id INTEGER, quantity INTEGER, total_amount REAL, order_date TEXT,
      FOREIGN KEY(customer_id) REFERENCES customers(id), FOREIGN KEY(product_id) REFERENCES products(id));
    """)
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", CUSTOMERS)
    random.seed(42)
    oid = 1
    for _ in range(120):
        pid = random.choice(PRODUCTS)[0]
        price = dict((p[0], p[2]) for p in [(x[0], x[0], x[3]) for x in PRODUCTS])[pid] if False else [p[3] for p in PRODUCTS if p[0]==pid][0]
        qty = random.randint(1, 5)
        cid = random.randint(1, 5)
        cur.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", (oid, cid, pid, qty, round(price*qty,2), f"2026-0{random.randint(1,9)}-{random.randint(10,28):02d}"))
        oid += 1
    con.commit(); con.close()
    return db_path

if __name__ == "__main__":
    print(setup())
