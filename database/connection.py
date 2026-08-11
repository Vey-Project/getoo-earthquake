"""
database/connection.py - Koneksi dan inisialisasi database SQLite
"""
import sqlite3
import os
from config import DATABASE_PATH


def get_connection():
    """Mendapatkan koneksi database"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Membuat tabel jika belum ada"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS server_config (
            server_id TEXT PRIMARY KEY,
            channel_id TEXT NOT NULL,
            min_magnitude REAL DEFAULT 4.5,
            region TEXT,
            language TEXT DEFAULT 'id',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS earthquake_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            earthquake_id TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'usgs',
            magnitude REAL,
            location TEXT,
            latitude REAL,
            longitude REAL,
            depth REAL,
            time TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(earthquake_id, source)
        );

        CREATE TABLE IF NOT EXISTS tsunami_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            earthquake_id TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(earthquake_id, source)
        );
    """)

    conn.commit()
    conn.close()