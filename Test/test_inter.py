import socket
import time
import sys
from thread import *
host = 'localhost'
port = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((host, port))
except s.error as msg:
    print 'Binding failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

try:
    s.listen(0)
except s.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()




def client_thread(conn):
    reply = ""
    conn.send('Welcome to the server. Type something and hit enter\n')

    while True:
        s.settimeout(5)
        try:
            data = conn.recv(1024)
        except s.timeout:
            print "Got timeout!"
            conn.close()
            sys.exit()
        if '/r' in data or '/n' in data:
            data = data.replace('/r', "")
            data = data.replace('/n', "")

        if data == "IP":
            reply = (str(clientIP)+"\n")
        elif data == "TIME":
            reply = (time.ctime(time.time())+"\n")
        elif data == "EXIT":
            conn.close()
            s.close()
            False
            break
        elif data == "\r\n":
            try:
                conn.sendall(reply)
            except s.error:
                print 'Message seding to client: failed'
                sys.exit(0)
        else:
            reply = "Invalid command!\n"





while True:
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    clientIP = addr[0]
    start_new_thread(client_thread, (conn,))

conn.close()
s.shutdown(1)
