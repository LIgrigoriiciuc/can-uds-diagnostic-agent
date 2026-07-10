import ctypes

lib = ctypes.CDLL('./libcancodec.so')

# Tell ctypes the function signatures (types matter...)
lib.decode_rpm.restype = ctypes.c_double
lib.decode_rpm.argtypes = [ctypes.c_uint8, ctypes.c_uint8]

lib.decode_coolant.restype = ctypes.c_double
lib.decode_coolant.argtypes = [ctypes.c_uint8]

# Test against a captured frame: D9 12 82 00 ... so on
rpm = lib.decode_rpm(0xD9, 0x12)
temp = lib.decode_coolant(0x82)

print(f"RPM: {rpm}, Coolant: {temp}")
