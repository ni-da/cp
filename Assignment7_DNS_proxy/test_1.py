import struct

a = struct.pack('hhl', 1, 2, 3)
b = struct.unpack('hhl', a)

print(b)
