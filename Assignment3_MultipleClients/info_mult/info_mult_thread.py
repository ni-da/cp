import socket
import sys
import time
from threading import Thread

# --- returns ip addres ---
def get_ip_from_adr(addr):
    cliIp, cliPort = addr
    return cliIp


# --- return the correct output ---
def run_command(cliM, conn, addr):
    if cliM == "":
        pass
    elif cliM == "IP":
        reply = (str(get_ip_from_adr(addr)) + "\r\n")
        conn.sendall(reply)
    elif cliM == "TIME":
        reply = (str(time.ctime()) + "\r\n")
        conn.sendall(reply)
    elif cliM == "EXIT":
        for connection in connections:
            connection.close()
            connections.remove(connection)
        s.close()
        sys.exit()
    else:
        reply = (str("UNKNOWN COMMAND") + "\r\n")
        conn.sendall(reply)


# --- handle connections, used to create threads ---
def handle_client(conn, client_addr):
    conn.settimeout(30)
    cliM = ""
    while True:
        try:
            data = conn.recv(1024)
        except socket.timeout:
            print "Client got timeout"
            conn.sendall("Got timeout! Disconnecting... ")
            break

        if not data:
            break
        else:
            if '\xff\xfb\x1f\xff\xfb' in data:  # needed for putty first sending line
                cliM = ""
                pass
            else:
                cliM += data
                if '\r\n' in data or '\n' in data:
                    commands = cliM.split('\n')
                    for c in commands:
                        c = c.replace("\r", "")
                        run_command(c, conn, client_addr)
                    cliM = ""
    conn.close()


host = 'localhost'
port = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind socket to local host and port
try:
    s.bind((host, port))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# Start listening on socket
try:
    s.listen(10)
except socket.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    s.close()
    sys.exit()

connections = []
while 1:
    # wait to accept a connection -> blocking call
    conn, client_addr = s.accept()
    connections.append(conn)
    t = Thread(target=handle_client, args=(conn, client_addr))
    t.start()
s.close()
