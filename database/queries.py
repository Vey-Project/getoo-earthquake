"""
database/queries.py - Query CRUD untuk database
"""
from database.connection import get_connection


# ============ SERVER CONFIG ============

def get_server_config(server_id: str):
    """Ambil konfigurasi server"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM server_config WHERE server_id = ?", (server_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def set_server_channel(server_id: str, channel_id: str):
    """Set channel notifikasi"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_config (server_id, channel_id, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(server_id) DO UPDATE SET
            channel_id = excluded.channel_id,
            updated_at = CURRENT_TIMESTAMP
    """, (server_id, channel_id))
    conn.commit()
    conn.close()


def set_server_magnitude(server_id: str, magnitude: float):
    """Set threshold magnitudo"""
    conn = get_connection()
    cursor = conn.cursor()
    # Cek dulu apakah sudah ada
    cursor.execute("SELECT 1 FROM server_config WHERE server_id = ?", (server_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
            UPDATE server_config SET min_magnitude = ?, updated_at = CURRENT_TIMESTAMP
            WHERE server_id = ?
        """, (magnitude, server_id))
    else:
        cursor.execute("""
            INSERT INTO server_config (server_id, channel_id, min_magnitude, updated_at)
            VALUES (?, '', ?, CURRENT_TIMESTAMP)
        """, (server_id, magnitude))
    conn.commit()
    conn.close()


def set_server_region(server_id: str, region: str):
    """Set filter wilayah"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM server_config WHERE server_id = ?", (server_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
            UPDATE server_config SET region = ?, updated_at = CURRENT_TIMESTAMP
            WHERE server_id = ?
        """, (region, server_id))
    else:
        cursor.execute("""
            INSERT INTO server_config (server_id, channel_id, region, updated_at)
            VALUES (?, '', ?, CURRENT_TIMESTAMP)
        """, (server_id, region))
    conn.commit()
    conn.close()


def get_all_active_servers():
    """Dapatkan semua server yang aktif (punya channel)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM server_config WHERE channel_id IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============ EARTHQUAKE LOG ============

def is_earthquake_sent(earthquake_id: str, source: str = "usgs") -> bool:
    """Cek apakah gempa sudah pernah dikirim"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM earthquake_log WHERE earthquake_id = ? AND source = ?",
        (earthquake_id, source)
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result


def log_earthquake(earthquake_id: str, source: str, magnitude: float,
                   location: str, lat: float, lon: float, depth: float, time: str):
    """Catat gempa yang sudah dikirim"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO earthquake_log
        (earthquake_id, source, magnitude, location, latitude, longitude, depth, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (earthquake_id, source, magnitude, location, lat, lon, depth, time))
    conn.commit()
    conn.close()


def get_recent_earthquakes(limit: int = 5):
    """Ambil gempa terakhir yang sudah dikirim"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM earthquake_log
        ORDER BY sent_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_tsunami_sent(earthquake_id: str, source: str) -> bool:
    """Cek apakah tsunami sudah dikirim"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM tsunami_log WHERE earthquake_id = ? AND source = ?",
        (earthquake_id, source)
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result


def log_tsunami(earthquake_id: str, source: str, message: str):
    """Catat peringatan tsunami yang sudah dikirim"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO tsunami_log (earthquake_id, source, message)
        VALUES (?, ?, ?)
    """, (earthquake_id, source, message))
    conn.commit()
    conn.close()