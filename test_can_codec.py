import ctypes
import pytest

lib = ctypes.CDLL('./libcancodec.so')
#types matter
lib.decode_rpm.restype = ctypes.c_double
lib.decode_rpm.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
lib.decode_coolant.restype = ctypes.c_double
lib.decode_coolant.argtypes = [ctypes.c_uint8]

def test_decode_rpm_matches_known_frame():
    # from captured frame: D9 12 82 ...
    rpm = lib.decode_rpm(0xD9, 0x12)
    assert rpm == pytest.approx(1206.25)

def test_decode_coolant_matches_known_frame():
    temp = lib.decode_coolant(0x82)
    assert temp == pytest.approx(90.0)
