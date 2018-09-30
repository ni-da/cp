import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 2000))

while 1:
    data = raw_input("Data: ")
    s.sendall(data)
    msg = s.recv(60)
    print "Server says: ", msg
    if data == "GO":
        break
