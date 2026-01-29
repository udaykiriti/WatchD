import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "sysguard.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    type TEXT,
                    message TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    cpu REAL,
                    memory REAL,
                    disk REAL
                )''')
    conn.commit()
    conn.close()

def log_alert(alert_type, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO alerts (timestamp, type, message) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), alert_type, message))
    conn.commit()
    conn.close()

def log_metrics(cpu, memory, disk):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO metrics (timestamp, cpu, memory, disk) VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), cpu, memory, disk))
    conn.commit()
    conn.close()

def get_recent_alerts(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, type, message FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
