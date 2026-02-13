# Python for Industrial IoT

Learning Python for edge computing in oil & gas. 2 weeks of fundamentals.

## Structure

```
├── day03-error-handling/    # try/except basics
├── day06-oop-protocols/     # classes for sensor protocols  
├── week2-csv-processing/    # cleaning historian exports
├── day11-store-and-forward/ # sqlite buffering
└── week2-complete/          # all together: IronClad gateway
```

## Progress

**Day 3** - Error handling so one bad sensor doesnt crash everything

**Day 6** - Using classes to support modbus/mqtt/opcua with same interface

**Week 2** - CSV processing for messy historian data

**Day 11** - SQLite store-and-forward for unreliable networks

**Week 2 Complete** - IronClad: gateway that combines all of the above

## Run any project

```bash
python sensor_reader.py
python protocol_gateway.py
python historian_processor.py
python store_forward.py
python ironclad_gateway.py
```

## Whats next

Docker
Azure IoT Hub
OPC-UA, Kubernetes

---

Part of my transition from software dev to oil & gas digital infrastructure.
