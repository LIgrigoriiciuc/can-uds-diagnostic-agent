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
SID_READ_DTC = 0x19
SID_READ_DTC_POS_RESPONSE = 0x59  # 0x19 + 0x40
SUBFUNC_REPORT_DTC_BY_STATUS_MASK = 0x02
#real DTCs: 2-byte codes (e.g. P0171) + a 1-byte status.
#Status byte 0x08 = "confirmed DTC" (simplified; real status
# bytes are a bitmask of multiple flags).
ACTIVE_DTCS = [
    (0x0171, 0x08),  #System Too Lean (Bank 1)
]
bus = can.interface.Bus(channel='vcan0', interface='socketcan')
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
            print(f"Replied to DID {hex(did)}")
        elif sid == SID_READ_DTC and data[1] == SUBFUNC_REPORT_DTC_BY_STATUS_MASK:
            #build response: [0x59, 0x02, statusAvailabilityMask, DTC1_hi, DTC1_lo, DTC1_status, DTC2_hi, ...]
            response_data = [SID_READ_DTC_POS_RESPONSE, SUBFUNC_REPORT_DTC_BY_STATUS_MASK, 0xFF]
            for code, status in ACTIVE_DTCS:
                response_data.append((code >> 8) & 0xFF)
                response_data.append(code & 0xFF)
                response_data.append(status)
            print(f"Reporting {len(ACTIVE_DTCS)} active DTC(s)")
        else:
            response_data = [SID_NEGATIVE_RESPONSE, sid, NRC_REQUEST_OUT_OF_RANGE]
        response_data += [0x00] * (8 - len(response_data))  # pad to 8 bytes
        response = can.Message(arbitration_id=RESPONSE_ID, data=response_data, is_extended_id=False)
        bus.send(response)
except KeyboardInterrupt:
    print("Stopped.")
finally:
    bus.shutdown()
