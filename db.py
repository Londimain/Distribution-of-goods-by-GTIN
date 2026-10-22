# -*- coding: utf-8 -*-
import sqlite3
import os
import json

# Функция для получения пути к БД (из settings.json или по умолчанию)
def get_db_path():
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                path = data.get('db_path', 'products.db')
                if path:
                    return path
        except Exception:
            pass
    return "products.db"

DB_NAME = get_db_path()

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

def get_db_mtime():
    """Возвращает время последнего изменения файла БД"""
    if os.path.exists(DB_NAME):
        return os.path.getmtime(DB_NAME)
    return 0