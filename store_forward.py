"""
Day 11 - Store and forward with SQLite

Problem: if network drops while sending to cloud, data is lost
Solution: save locally first, then sync when network is back

Using SQLite because:
- atomic writes (no corruption if power dies)
- easy to track what's been sent vs pending
"""

import sqlite3
import random
import time
from datetime import datetime


class DataBuffer:
    def __init__(self, db_path="buffer.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()
    
    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY,
                sensor_id TEXT,
                value REAL,
                timestamp TEXT,
                sent INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def store(self, sensor_id, value):
        """save reading locally first - never trust network"""
        self.conn.execute(
            "INSERT INTO readings (sensor_id, value, timestamp, sent) VALUES (?, ?, ?, 0)",
            (sensor_id, value, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_pending(self, limit=10):
        """get readings that havent been sent yet"""
        cur = self.conn.execute(
            "SELECT * FROM readings WHERE sent = 0 ORDER BY id LIMIT ?",
            (limit,)
        )
        return cur.fetchall()
    
    def mark_sent(self, ids):
        """mark as sent after successful upload"""
        if not ids:
            return
        placeholders = ",".join(["?"] * len(ids))
        self.conn.execute(
            f"UPDATE readings SET sent = 1 WHERE id IN ({placeholders})",
            ids
        )
        self.conn.commit()
    
    def stats(self):
        cur = self.conn.execute("SELECT COUNT(*) as total, SUM(sent) as sent FROM readings")
        row = cur.fetchone()
        total = row["total"]
        sent = row["sent"] or 0
        return {"total": total, "sent": sent, "pending": total - sent}
    
    def close(self):
        self.conn.close()


def fake_cloud_send(readings):
    """simulate cloud upload - fails sometimes"""
    if random.random() < 0.7:
        return True
    return False


if __name__ == "__main__":
    print("Store-and-Forward Demo\n")
    
    buffer = DataBuffer("demo.db")
    
    # collect some readings
    print("Collecting sensor data...")
    for i in range(10):
        buffer.store(f"sensor_{i % 3}", round(random.uniform(100, 150), 2))
    
    print(f"Stored: {buffer.stats()}\n")
    
    # try to sync
    print("Attempting cloud sync...")
    attempts = 0
    while buffer.stats()["pending"] > 0 and attempts < 5:
        attempts += 1
        pending = buffer.get_pending(5)
        
        if fake_cloud_send(pending):
            ids = [r["id"] for r in pending]
            buffer.mark_sent(ids)
            print(f"  Sent {len(ids)} readings")
        else:
            print(f"  Network failed - will retry")
        
        time.sleep(0.3)
    
    print(f"\nFinal: {buffer.stats()}")
    
    buffer.close()
    
    import os
    os.remove("demo.db")
