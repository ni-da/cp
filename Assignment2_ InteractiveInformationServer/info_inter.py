import socket
import time
import sys


def close_server(conn, s):
    conn.close
    s.close
    sys.exit()


def run_command(cliM):
    if cliM == "":
        pass
    elif cliM == "IP":
        reply = (str(cliAdr) + "\r\n")
        conn.sendall(reply)
    elif cliM == "TIME":
        reply = (str(time.ctime()) + "\r\n")
        conn.sendall(reply)
    elif cliM == "EXIT":
        close_server(conn, s)
    else:
        reply = (str("UNKNOWN COMMAND") + "\r\n")
        conn.sendall(reply)


host = 'localhost'
port = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((host, port))
except socket.error as msg:
    print 'Binding failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()

try:
    s.listen(1)
except socket.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()

while 1:
    conn, addr = s.accept()  # returns a NEW socket in conn and address in addr
    cliAdr, cliPort = addr
    # print("Connected to: ", cliAdr)

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
                        run_command(c)
                    cliM = ""
    # print("Disconnected to: ", cliAdr)
    conn.close()
s.close()
