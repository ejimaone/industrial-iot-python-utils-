"""
Week 2 Complete - IronClad Edge Gateway

Putting together everything from the last 2 weeks:
- error handling (day 3)
- OOP for protocols (day 6)  
- sqlite buffering (day 11)
- os module for monitoring

This is a simplified version. Real one would use pymodbus, azure-iot-device, etc
"""

import sqlite3
import shutil
import random
import time
import logging
from datetime import datetime
from abc import ABC, abstractmethod

# basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
log = logging.getLogger("ironclad")


# --- Sensors (from day 6) ---

class Sensor(ABC):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.connected = False
    
    @abstractmethod
    def connect(self): pass
    
    @abstractmethod
    def read(self): pass


class ModbusSensor(Sensor):
    def connect(self):
        # simulate - real code would use pymodbus
        if random.random() > 0.1:
            self.connected = True
            log.info(f"Connected: {self.name}")
            return True
        log.warning(f"Connect failed: {self.name}")
        return False
    
    def read(self):
        if not self.connected:
            return None
        
        try:
            if random.random() < 0.05:
                raise TimeoutError("timeout")
            
            return {
                "sensor": self.name,
                "value": round(random.uniform(100, 150), 2),
                "timestamp": datetime.now().isoformat()
            }
        except TimeoutError:
            log.warning(f"Read timeout: {self.name}")
            return None


# --- Buffer (from day 11) ---

class Buffer:
    def __init__(self, path="ironclad.db"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY,
                sensor TEXT,
                value REAL,
                timestamp TEXT,
                sent INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def store(self, reading):
        if not reading:
            return
        self.conn.execute(
            "INSERT INTO data (sensor, value, timestamp) VALUES (?, ?, ?)",
            (reading["sensor"], reading["value"], reading["timestamp"])
        )
        self.conn.commit()
    
    def get_pending(self, n=20):
        cur = self.conn.execute(
            "SELECT * FROM data WHERE sent=0 ORDER BY id LIMIT ?", (n,)
        )
        return cur.fetchall()
    
    def mark_sent(self, ids):
        if not ids:
            return
        ph = ",".join(["?"] * len(ids))
        self.conn.execute(f"UPDATE data SET sent=1 WHERE id IN ({ph})", ids)
        self.conn.commit()
    
    def pending_count(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM data WHERE sent=0")
        return cur.fetchone()[0]
    
    def close(self):
        self.conn.close()


# --- System monitor (os module stuff) ---

def check_disk():
    """check if we have enough disk space"""
    total, used, free = shutil.disk_usage(".")
    pct = (free / total) * 100
    if pct < 10:
        log.warning(f"Low disk: {pct:.1f}% free")
    return pct


# --- Cloud sync (simulated) ---

def send_to_cloud(batch):
    """fake cloud send - 80% success rate"""
    if random.random() < 0.8:
        return True
    return False


# --- Main gateway ---

class Gateway:
    def __init__(self):
        self.sensors = []
        self.buffer = Buffer()
    
    def add_sensor(self, sensor):
        self.sensors.append(sensor)
    
    def connect_all(self):
        for s in self.sensors:
            s.connect()
    
    def collect(self):
        """read all sensors, store locally"""
        count = 0
        for s in self.sensors:
            reading = s.read()
            if reading:
                self.buffer.store(reading)
                count += 1
        return count
    
    def sync(self):
        """try to send pending data to cloud"""
        pending = self.buffer.get_pending()
        if not pending:
            return 0
        
        if send_to_cloud(pending):
            ids = [r["id"] for r in pending]
            self.buffer.mark_sent(ids)
            return len(ids)
        return 0
    
    def health_check(self):
        disk = check_disk()
        pending = self.buffer.pending_count()
        connected = sum(1 for s in self.sensors if s.connected)
        
        return {
            "disk_free": f"{disk:.1f}%",
            "pending": pending,
            "sensors": f"{connected}/{len(self.sensors)}"
        }
    
    def shutdown(self):
        self.buffer.close()


if __name__ == "__main__":
    print("=" * 50)
    print("IronClad Edge Gateway")
    print("=" * 50)
    
    gw = Gateway()
    
    # add some sensors
    gw.add_sensor(ModbusSensor("pressure_1", "192.168.1.10"))
    gw.add_sensor(ModbusSensor("pressure_2", "192.168.1.11"))
    gw.add_sensor(ModbusSensor("temp_1", "192.168.1.20"))
    
    print("\n--- Connecting ---")
    gw.connect_all()
    
    print("\n--- Collecting data ---")
    for i in range(5):
        n = gw.collect()
        print(f"Cycle {i+1}: collected {n} readings")
        time.sleep(0.2)
    
    print("\n--- Syncing to cloud ---")
    for i in range(3):
        sent = gw.sync()
        if sent:
            print(f"Sent {sent} readings")
        else:
            print("Sync failed or nothing pending")
        time.sleep(0.2)
    
    print("\n--- Health check ---")
    h = gw.health_check()
    print(f"Disk: {h['disk_free']}")
    print(f"Pending: {h['pending']}")
    print(f"Sensors: {h['sensors']}")
    
    gw.shutdown()
    
    # cleanup demo db
    import os
    os.remove("ironclad.db")
    
    print("\n" + "=" * 50)
    print("Done. Next: Docker + Azure IoT Hub")
