"""
Day 6 - Trying OOP for different sensor protocols

The idea: make a base class so I can add modbus, opcua, mqtt later
without rewriting everything
"""

from abc import ABC, abstractmethod
from datetime import datetime
import random


class Sensor(ABC):
    """base class - all sensors need these methods"""
    
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.connected = False
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def read(self):
        pass
    
    def disconnect(self):
        self.connected = False


class ModbusSensor(Sensor):
    """
    simulating modbus for now
    will use pymodbus later when I get to that part of the roadmap
    """
    
    def connect(self):
        # pretend to connect
        if random.random() > 0.1:
            self.connected = True
            print(f"Connected: {self.name}")
            return True
        else:
            print(f"Failed to connect: {self.name}")
            return False
    
    def read(self):
        if not self.connected:
            return None
        
        # simulate reading with possible failures
        try:
            if random.random() < 0.05:
                raise TimeoutError("read timeout")
            
            return {
                "sensor": self.name,
                "value": round(random.uniform(100, 150), 2),
                "unit": "PSI",
                "timestamp": datetime.now().isoformat()
            }
        except TimeoutError:
            print(f"Timeout reading {self.name}")
            return None


class MqttSensor(Sensor):
    """mqtt version - same interface different protocol"""
    
    def __init__(self, name, address, topic):
        super().__init__(name, address)
        self.topic = topic
    
    def connect(self):
        # mqtt is usually more reliable
        if random.random() > 0.02:
            self.connected = True
            print(f"Connected: {self.name} on {self.topic}")
            return True
        return False
    
    def read(self):
        if not self.connected:
            return None
        
        return {
            "sensor": self.name,
            "value": round(random.uniform(100, 150), 2),
            "unit": "PSI",
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # test with both types
    sensors = [
        ModbusSensor("pressure_1", "192.168.1.10:502"),
        ModbusSensor("pressure_2", "192.168.1.11:502"),
        MqttSensor("temp_1", "mqtt://broker", "sensors/temp/1"),
    ]
    
    print("Connecting...\n")
    for s in sensors:
        s.connect()
    
    print("\nReading...\n")
    for s in sensors:
        data = s.read()
        if data:
            print(f"{data['sensor']}: {data['value']} {data['unit']}")
        else:
            print(f"{s.name}: no data")
    
    print("\nDone. Same code works for modbus and mqtt.")
