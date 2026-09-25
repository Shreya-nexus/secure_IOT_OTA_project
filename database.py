import sqlite3
import os
from flask import g, current_app
from config import Config

def get_db(db_path=None):
    """
    Get or create SQLite database connection.
    Uses Flask application context 'g' if available.
    """
    if db_path is None:
        try:
            if current_app:
                db_path = current_app.config.get("DATABASE_PATH", Config.DATABASE_PATH)
            else:
                db_path = Config.DATABASE_PATH
        except RuntimeError:
            db_path = Config.DATABASE_PATH
    
    path = db_path
    
    # Ensure directory containing database exists
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


    try:
        # Check if running within Flask application context
        if g:
            if 'db' not in g:
                g.db = sqlite3.connect(path)
                g.db.row_factory = sqlite3.Row
            return g.db
    except RuntimeError:
        # Outside Flask context (e.g. CLI, tests, stand-alone scripts)
        pass

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(e=None):
    """Close the database connection at the end of the request."""
    try:
        db = g.pop('db', None)
        if db is not None:
            db.close()
    except RuntimeError:
        pass

def init_db(db_path=None):
    """Initialize database tables according to requirements."""
    conn = get_db(db_path)
    cursor = conn.cursor()

    # Table 1: DEVICES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DEVICES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE NOT NULL,
        device_name TEXT NOT NULL,
        current_firmware_version TEXT NOT NULL,
        api_token_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'offline',
        last_seen TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Table 2: FIRMWARE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FIRMWARE (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        sha256_hash TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        uploaded_at TEXT NOT NULL,
        is_latest INTEGER NOT NULL DEFAULT 0
    );
    """)

    # Table 3: UPDATE_LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UPDATE_LOGS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        old_version TEXT NOT NULL,
        new_version TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    
    # Close if manually instantiated outside context
    try:
        if 'g' not in globals() or not g:
            conn.close()
    except Exception:
        conn.close()
