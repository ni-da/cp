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
# accept can throw socket.timeout
s.settimeout(5.0)
try:
    conn, addr = s.accept()
except socket.timeout:
    print("Time out for connecting!")

# recv can throw socket.timeout
conn.settimeout(5.0)
conn.recv(1024)

sock.close()
