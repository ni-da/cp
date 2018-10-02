import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 2000))

s.sendall("TIME\r\n")
msg = s.recv(60)
print msg

s.sendall("IP\r\n")
msg = s.recv(60)
print msg

s.sendall("Something\r\n")
msg = s.recv(60)
print msg

# s.sendall("EXIT")
# s.close()
