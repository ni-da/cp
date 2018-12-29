import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('ftp.dlptest.com', 21))

msg = s.recv(1024)
print msg