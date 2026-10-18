# -*- coding: utf-8 -*-
import sqlite3

DB_NAME = "products.db"

def init_db():
    with sqlite3.connect(DB_NAME) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                volume TEXT DEFAULT '',
                gtin TEXT NOT NULL UNIQUE
            )
        """)
        cursor = con.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'volume' not in columns:
            con.execute("ALTER TABLE products ADD COLUMN volume TEXT DEFAULT ''")

def get_products():
    with sqlite3.connect(DB_NAME) as con:
        return con.execute("SELECT id, name, volume, gtin FROM products ORDER BY id").fetchall()

def add_product(name, volume, gtin):
    with sqlite3.connect(DB_NAME) as con:
        con.execute("INSERT INTO products (name, volume, gtin) VALUES (?, ?, ?)", (name, volume, gtin))

def update_product(pid, name, volume, gtin):
    with sqlite3.connect(DB_NAME) as con:
        con.execute("UPDATE products SET name=?, volume=?, gtin=? WHERE id=?", (name, volume, gtin, pid))

def delete_product(pid):
    with sqlite3.connect(DB_NAME) as con:
        con.execute("DELETE FROM products WHERE id=?", (pid,))