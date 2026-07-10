import can
import time

#Data Identifier SCHEME
#custom-defined for this project, mimicking how a real manufacturer would reserve a range of DIDs for their data
#real ECUs would be a spec sheet shared between diagnostic tool and ECU teams

DID_ENGINE_RPM = 0x0C0C  
DID_COOLANT_TEMP = 0x0505 

# UDS service IDs
SID_READ_DATA_BY_ID = 0x22
SID_READ_DATA_BY_ID_POS_RESPONSE = 0x62  #request SID + 0x40
SID_NEGATIVE_RESPONSE = 0x7F

#Negative Response Codes (subset)
NRC_REQUEST_OUT_OF_RANGE = 0x31

# Diagnostic CAN IDs
REQUEST_ID  = 0x7E0
RESPONSE_ID = 0x7E8

bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

#simulating ECU's current known values... real ECU: sensor reads
current_rpm = 1500.0
current_coolant = 88.0

print(f"UDS ECU responder listening on {hex(REQUEST_ID)}, replying on {hex(RESPONSE_ID)}...")

try:
    while True:
        msg = bus.recv(timeout=1.0)
        if msg is None or msg.arbitration_id != REQUEST_ID:
            continue

        data = msg.data
        sid = data[0]

        if sid == SID_READ_DATA_BY_ID:
            did = (data[1] << 8) | data[2]  #DID is 2 bytes, big-endian in UDS

            if did == DID_ENGINE_RPM:
                raw = int(current_rpm / 0.25)  #reverse the DBC scale factor
                response_data = [
                    SID_READ_DATA_BY_ID_POS_RESPONSE,
                    data[1], data[2],
                    raw & 0xFF, (raw >> 8) & 0xFF
                ]
            elif did == DID_COOLANT_TEMP:
                raw = int(current_coolant + 40)  #reverse the DBC offset
                response_data = [
                    SID_READ_DATA_BY_ID_POS_RESPONSE,
                    data[1], data[2],
                    raw
                ]
            else:
                #unknown DID -> negative response
                response_data = [SID_NEGATIVE_RESPONSE, SID_READ_DATA_BY_ID, NRC_REQUEST_OUT_OF_RANGE]

            response_data += [0x00] * (8 - len(response_data))  # pad to 8 bytes
            response = can.Message(arbitration_id=RESPONSE_ID, data=response_data, is_extended_id=False)
            bus.send(response)
            print(f"Replied to DID {hex(did)}")

except KeyboardInterrupt:
    print("Stopped.")
finally:
    bus.shutdown()
