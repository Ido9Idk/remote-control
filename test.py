import struct
a = struct.pack('!I', 1) + struct.pack('!I', 3)
print("header: ", a[:4])