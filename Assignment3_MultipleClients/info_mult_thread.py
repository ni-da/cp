import socket
import sys
import time
from thread import *

# --- close everything ---
def close_server(conn, s):
    conn.close
    s.close
    sys.exit()


# --- return the correct output ---
def run_command(cliM, conn):
    if cliM == "":
        pass
    elif cliM == "IP":
        # reply = (str(cliAdr) + "\r\n")
        reply = (str("ADR") + "\r\n")
        conn.sendall(reply)
    elif cliM == "TIME":
        reply = (str(time.ctime()) + "\r\n")
        conn.sendall(reply)
    elif cliM == "EXIT":
        print("Got to EXIT!")
        close_server(conn, s)
    else:
        reply = (str("UNKNOWN COMMAND") + "\r\n")
        conn.sendall(reply)


# --- handle connections, used to create threads ---
def clientthread(conn):
    # Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n')  # send only takes string

    # infinite loop so that function do not terminate and thread do not end.
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
                        run_command(c, conn)
                    cliM = ""

    # came out of loop
    conn.close()


host = 'localhost'
port = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((host, port))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

# Start listening on socket
try:
    s.listen(10)
    print 'Socket now listening'
except socket.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()

# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the
    # tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

s.close()
