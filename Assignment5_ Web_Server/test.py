import socket
import time
import sys


def close_server(conn, s):
    conn.close
    s.close
    sys.exit()


host = 'localhost'
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

s.listen(1)
while 1:
    conn, addr = s.accept()  # returns a NEW socket
    cliAdr, cliPort = addr
    data = conn.recv(1000)  # should receive request from client. (GET ....)
    print(data)
    conn.send('HTTP/1.0 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('\n')  # header and body should be separated by additional newline
    conn \
        .send("""
            <html>
            <body>
            <h1>Hello World</h1> this is my server!
            </body>
            </html>
        """)  # Use triple-quote string.
    # conn.close()
s.close()
