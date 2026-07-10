import can
import cantools
import time
import random

#loading the DBC (to encode real signal values into raw bytes)
db = cantools.database.load_file('engine.dbc')
engine_msg = db.get_message_by_name('EngineData')

#connecting to vcan0 interface via SocketCAN
bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

print("ECU simulator running. Sending EngineData on vcan0...")

try:
    while True:
        rpm = random.uniform(800, 4000) #idle to mid-range RPM
        coolant = random.uniform(70, 95) # normal operating temp range (celsius)

        data = engine_msg.encode({'EngineRPM': rpm, 'CoolantTemp': coolant})
        msg = can.Message(arbitration_id=engine_msg.frame_id, data=data, is_extended_id=False)

        bus.send(msg)
        print(f"Sent: RPM={rpm:.1f} CoolantTemp={coolant:.1f}°C")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")

