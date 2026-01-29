import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "sysguard.db")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        type TEXT,
                        message TEXT
                    )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        cpu REAL,
                        memory REAL,
                        disk REAL
                    )''')
        conn.commit()

def log_metrics(cpu, memory, disk):
    """Log system metrics to database"""
    with get_db_connection() as conn:
        conn.execute("INSERT INTO metrics (timestamp, cpu, memory, disk) VALUES (?, ?, ?, ?)",
                     (datetime.now().isoformat(), cpu, memory, disk))
        conn.commit()

def get_recent_alerts(limit=10):
    """Retrieve recent alerts from database"""
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT timestamp, type, message FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
