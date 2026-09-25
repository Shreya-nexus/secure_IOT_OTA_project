from datetime import datetime, timezone
from database import get_db

def get_iso_timestamp():
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

class DeviceModel:
    @staticmethod
    def create(device_id, device_name, current_firmware_version, api_token_hash, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        now = get_iso_timestamp()
        cursor.execute("""
            INSERT INTO DEVICES (device_id, device_name, current_firmware_version, api_token_hash, status, last_seen, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (device_id, device_name, current_firmware_version, api_token_hash, 'offline', None, now))
        conn.commit()
        return DeviceModel.get_by_device_id(device_id, db_path=db_path)

    @staticmethod
    def get_by_device_id(device_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_token_hash(token_hash, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE api_token_hash = ?", (token_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_all(db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update_heartbeat(device_id, status="online", db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        now = get_iso_timestamp()
        cursor.execute("""
            UPDATE DEVICES
            SET status = ?, last_seen = ?
            WHERE device_id = ?
        """, (status, now, device_id))
        conn.commit()
        return DeviceModel.get_by_device_id(device_id, db_path=db_path)

    @staticmethod
    def update_firmware_version(device_id, new_version, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE DEVICES
            SET current_firmware_version = ?
            WHERE device_id = ?
        """, (new_version, device_id))
        conn.commit()
        return DeviceModel.get_by_device_id(device_id, db_path=db_path)


class FirmwareModel:
    @staticmethod
    def create(version, filename, file_path, sha256_hash, file_size, is_latest=0, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        now = get_iso_timestamp()
        
        # If marked as latest, reset other firmware entries
        if is_latest:
            cursor.execute("UPDATE FIRMWARE SET is_latest = 0")

        cursor.execute("""
            INSERT INTO FIRMWARE (version, filename, file_path, sha256_hash, file_size, uploaded_at, is_latest)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (version, filename, file_path, sha256_hash, file_size, now, 1 if is_latest else 0))
        conn.commit()
        return FirmwareModel.get_by_version(version, db_path=db_path)

    @staticmethod
    def get_all(db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FIRMWARE ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_version(version, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FIRMWARE WHERE version = ?", (version,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_latest(db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FIRMWARE WHERE is_latest = 1 LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # Fallback to absolute highest entry by ID/uploaded_at if no flag set
        cursor.execute("SELECT * FROM FIRMWARE ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def set_latest(version, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE FIRMWARE SET is_latest = 0")
        cursor.execute("UPDATE FIRMWARE SET is_latest = 1 WHERE version = ?", (version,))
        conn.commit()


class UpdateLogModel:
    @staticmethod
    def create(device_id, old_version, new_version, status, message="", db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        now = get_iso_timestamp()
        cursor.execute("""
            INSERT INTO UPDATE_LOGS (device_id, old_version, new_version, status, message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (device_id, old_version, new_version, status, message, now))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all(db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UPDATE_LOGS ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_device_id(device_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UPDATE_LOGS WHERE device_id = ? ORDER BY id DESC", (device_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
