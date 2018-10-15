from socket import *
import time
import sys

address = 'localhost'
port = 2000
pong_server_address = (address, port)

ping_socket = socket(AF_INET, SOCK_DGRAM)
# ping_socket.setblocking(0)  # non-blocking


for i in range(1, 6):
    ping_messge = "PING-" + str(i)
    while True:
        try:
            ping_socket.sendto(ping_messge, pong_server_address)
            break
        except:
            pass

ping_sent_at = time.clock()
pong_wait_until = ping_sent_at + 5  # seconds


def timeout(wait_until):
    if time.clock() > wait_until:
        ping_socket.close()
        print "Packet lost"
        sys.exit(0)


def receive_pong():
    is_socket_closed = False
    try:
        pong_message, pong_server_address = ping_socket.recvfrom(1024)
        print(pong_message)
        pong_received_at = time.clock()
        ping_socket.close()
        is_socket_closed = True
        round_trip_time = (pong_received_at - ping_sent_at)
        print(round_trip_time)
        print "RTT (Round Trip Time) = {0:.6f}s".format(round_trip_time)
    except:
        pass
    if is_socket_closed:
        sys.exit(0)


while True:
    receive_pong()
    timeout(pong_wait_until)
