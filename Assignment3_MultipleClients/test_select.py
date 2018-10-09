import socket
import sys
import select



host = 'localhost'
port = 2000

sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # moet sws s
sock_listen.setblocking(0)
# Bind socket to local host and port
try:
    sock_listen.bind((host, port))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

# Start listening on socket
try:
    sock_listen.listen(10)
    print 'Socket now listening'
except socket.error as msg:
    print 'Cant listen to the client.' + str(msg[0]) + ' Message ' + msg[1]
    s.close
    sys.exit()


list_sockets = [sock_listen]
list_sockets_connected_clients = []
message_list = {}
sock_listen.setblocking(10)
list_sockets += list_sockets_connected_clients


