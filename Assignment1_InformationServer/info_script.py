import socket
import time
import sys


def close_server(conn, s):
    conn.close
    s.close
    sys.exit()


host = 'localhost'
port = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

s.listen(1)
while 1:
    conn, addr = s.accept()  # returns a NEW socket
    cliAdr, cliPort = addr
    while True:
        data = conn.recv(1024)
        if data == "IP":
            conn.sendall(cliAdr)
        elif data == "TIME":
            conn.sendall(time.ctime())
        elif data == "EXIT":
            close_server(conn, s)
            break
        if not data:
            break
    conn.close()
s.close()
