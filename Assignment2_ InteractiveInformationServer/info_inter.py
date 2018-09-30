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

try:
    s.bind((host, port))
except s.error as msg:
    print 'Binding failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()

try:
    s.listen(1)
except s.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()

while 1:
    conn, addr = s.accept()  # returns a NEW socket
    cliAdr, cliPort = addr
    print("Connected to: ", cliAdr)

    s.settimeout(30)
    cliM = ""
    while True:
        try:
            data = conn.recv(1024)
        except s.timeout:
            print "got timeout"
            close_server(conn, s)

        print(data, len(data))
        if not data:
            break
        else:
            if '\xff\xfb\x1f\xff\xfb' in data:  # nodig voor putty eerste regel
                print("YES")
                cliM = ""
                pass
            else:
                if data == '\r\n' or data == '\n':
                    if cliM == "IP":
                        reply = (str(cliAdr) + "\r\n")
                        conn.sendall(reply)
                        cliM = ""
                    elif cliM == "TIME":
                        reply = (str(time.ctime()) + "\r\n")
                        conn.sendall(reply)
                        cliM = ""
                    elif cliM == "EXIT":
                        close_server(conn, s)
                        break
                    else:
                        print(cliM, len(data))
                        reply = (str("UNKNOWN COMMAND") + "\r\n")
                        conn.sendall(reply)
                        cliM = ""
                else:
                    cliM += data
    print("Disconnected to: ", cliAdr)
    conn.close()
s.close()
