"""
Week 2 - CSV processing for historian exports

Historian systems export messy CSVs with missing data, bad quality flags, etc
This script cleans it up before we can use it
"""

import csv
from datetime import datetime


def create_test_data():
    """make a sample csv like what a historian would export"""
    data = [
        ["Timestamp", "Tag", "Value", "Quality"],
        ["2024-01-15 08:00:00", "WELL_A", "127.5", "Good"],
        ["2024-01-15 08:01:00", "WELL_A", "128.2", "Good"],
        ["", "WELL_A", "126.8", "Good"],  # missing timestamp
        ["2024-01-15 08:03:00", "WELL_A", "Bad", "Bad"],
        ["2024-01-15 08:04:00", "WELL_A", "-999", "Good"],  # sentinel value
        ["2024-01-15 08:05:00", "WELL_A", "129.1", "Good"],
        ["2024-01-15 08:06:00", "WELL_A", "ERROR", "Bad"],
        ["2024-01-15 08:07:00", "WELL_A", "130.5", "Good"],
    ]
    
    with open("test_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def is_valid_value(val):
    """check if value is actually usable"""
    if not val:
        return False
    
    # common bad values in historian exports
    bad = ["-999", "bad", "error", "null", "nan"]
    if val.lower() in bad:
        return False
    
    try:
        float(val)
        return True
    except:
        return False


def process_csv(filename):
    """read csv and filter out bad rows"""
    good = []
    bad_count = 0
    
    with open(filename) as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # skip if no timestamp
            if not row["Timestamp"]:
                bad_count += 1
                continue
            
            # skip bad quality
            if row["Quality"].lower() == "bad":
                bad_count += 1
                continue
            
            # skip invalid values
            if not is_valid_value(row["Value"]):
                bad_count += 1
                continue
            
            good.append({
                "timestamp": row["Timestamp"],
                "tag": row["Tag"],
                "value": float(row["Value"])
            })
    
    return good, bad_count


if __name__ == "__main__":
    create_test_data()
    
    print("Processing historian export...\n")
    
    clean_data, rejected = process_csv("test_data.csv")
    
    print(f"Clean rows: {len(clean_data)}")
    print(f"Rejected: {rejected}")
    
    if clean_data:
        values = [r["value"] for r in clean_data]
        print(f"\nStats:")
        print(f"  Min: {min(values)}")
        print(f"  Max: {max(values)}")
        print(f"  Avg: {sum(values)/len(values):.1f}")
    
    # cleanup
    import os
    os.remove("test_data.csv")
