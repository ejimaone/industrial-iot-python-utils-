"""
Day 3 - Learning error handling
Simulating sensor reads that can fail
"""

import random
from datetime import datetime


def read_sensor(sensor_id):
    # simulate random failures like real hardware would have
    fail = random.random()
    
    if fail < 0.1:
        raise TimeoutError("sensor timed out")
    elif fail < 0.15:
        raise ConnectionError("lost connection")
    elif fail < 0.2:
        return -999  # bad reading
    
    return round(random.uniform(100, 150), 2)


def read_sensor_safe(sensor_id):
    """wrap the read in try/except so one failure doesnt crash everything"""
    try:
        value = read_sensor(sensor_id)
        
        if value == -999:
            raise ValueError("got bad data from sensor")
        
        return {
            "sensor_id": sensor_id,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "status": "OK"
        }
    
    except TimeoutError as e:
        print(f"WARN: {sensor_id} - {e}")
        return {"sensor_id": sensor_id, "value": None, "status": "TIMEOUT"}
    
    except ConnectionError as e:
        print(f"WARN: {sensor_id} - {e}")
        return {"sensor_id": sensor_id, "value": None, "status": "CONN_ERR"}
    
    except ValueError as e:
        print(f"WARN: {sensor_id} - {e}")
        return {"sensor_id": sensor_id, "value": None, "status": "BAD_DATA"}


if __name__ == "__main__":
    print("Reading 20 sensors...\n")
    
    results = []
    for i in range(20):
        r = read_sensor_safe(f"PRESSURE_{i:03d}")
        results.append(r)
    
    # count failures
    ok = len([r for r in results if r["status"] == "OK"])
    failed = len(results) - ok
    
    print(f"\nDone: {ok} ok, {failed} failed")
    print("Point is: the script didnt crash even with failures")
