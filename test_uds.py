import can
import time
import pytest

SID_READ_DATA_BY_ID = 0x22
REQUEST_ID = 0x7E0
RESPONSE_ID = 0x7E8

DID_ENGINE_RPM = 0x0C0C
DID_COOLANT_TEMP = 0x0505

# these tests require uds_ecu.py to already be running in the background
@pytest.fixture
def bus():
    b = can.interface.Bus(channel='vcan0', interface='socketcan')
    yield b
    b.shutdown()

def send_and_receive(bus, did):
    did_hi = (did >> 8) & 0xFF
    did_lo = did & 0xFF
    request_data = [SID_READ_DATA_BY_ID, did_hi, did_lo, 0, 0, 0, 0, 0]
    msg = can.Message(arbitration_id=REQUEST_ID, data=request_data, is_extended_id=False)
    bus.send(msg)
    return bus.recv(timeout=2.0)

def test_read_engine_rpm(bus):
    response = send_and_receive(bus, DID_ENGINE_RPM)
    assert response is not None, "No response received (timeout) - is uds_ecu.py running?"
    assert response.data[0] == 0x62, "Expected positive response (0x62)"

    raw = response.data[3] | (response.data[4] << 8)
    rpm = raw * 0.25
    assert rpm == pytest.approx(1500.0)

def test_read_coolant_temp(bus):
    response = send_and_receive(bus, DID_COOLANT_TEMP)
    assert response is not None, "No response received (timeout) — is uds_ecu.py running?"
    assert response.data[0] == 0x62

    raw = response.data[3]
    temp = raw - 40
    assert temp == pytest.approx(88.0)

def test_unknown_did_returns_negative_response(bus):
    response = send_and_receive(bus, 0xFFFF)  # DID that doesn't exist
    assert response is not None
    assert response.data[0] == 0x7F, "Expected negative response (0x7F)"
