import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 2000))

s.sendall("TIME")
msg = s.recv(60)
print msg

s.sendall("IP")
msg = s.recv(60)
print msg

# s.sendall("Something")
# msg = s.recv(60)
# print msg

s.sendall("EXIT")
s.close()
