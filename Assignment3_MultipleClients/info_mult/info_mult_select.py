import select
import socket
import sys
import time


# --- returns ip addres ---
def get_ip_from_adr(addr):
    cliIp, cliPort = addr
    return cliIp


def run_command(conn, addr, cliM):
    if cliM == "":
        pass
    elif cliM == "IP":
        reply = (str(get_ip_from_adr(addr)) + "\r\n")
        conn.sendall(reply)
    elif cliM == "TIME":
        reply = (str(time.ctime()) + "\r\n")
        conn.sendall(reply)
    elif cliM == "EXIT":
        for conn in list_sockets:
            conn.close()
            server.close()
            sys.exit()
    else:
        reply = (str("UNKNOWN COMMAND") + "\r\n")
        conn.sendall(reply)


host = 'localhost'
port = 2000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((host, port))
server.listen(10)

list_sockets = [server]

while list_sockets:
    readable, writable, exceptional = select.select(
        list_sockets, [], list_sockets)

    for sock in readable:
        if sock is server:
            # Handle incoming client connection request
            connection, client_address = sock.accept()
            connection.setblocking(0)
            list_sockets.append(connection)
        else:
            sock.settimeout(30)
            cliM = ""
            while True:
                try:
                    data = sock.recv(1024)
                except socket.timeout:
                    print "Client got timeout"
                    sock.sendall("Got timeout! Disconnecting... ")
                    list_sockets.remove(sock)
                    sock.close()
                    break

                if not data:
                    list_sockets.remove(sock)
                    sock.close()
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
                                run_command(sock, client_address, c)
                            cliM = ""
    for e in exceptional:
        list_sockets.remove(e)
        e.close()
