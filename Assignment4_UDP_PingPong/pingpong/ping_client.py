import socket
import time
import sys

if len(sys.argv) > 2:
    total_pings_toSend = int(sys.argv[2])
else:
    total_pings_toSend = 4

address = sys.argv[1]
port = 2000
pong_server_address = (address, port)
ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

rrt_counter = 0
timeouts_counter = 0
pings_counter = 0
total_pings_sent = 0

while total_pings_sent < total_pings_toSend:
    if pings_counter == 1000:
        pings_counter = 0

    ping_socket.settimeout(5.0)
    ping_messge = "PING-" + str(pings_counter) + "!"
    ping_socket.sendto(ping_messge, pong_server_address)
    ping_sent_at = time.time()

    try:
        pong_message, pong_server_address = ping_socket.recvfrom(1024)
        pong_received_at = time.time()
        round_trip_time = (pong_received_at - ping_sent_at)
        round_trip_time = int(round(round_trip_time * 1000))
        print(str(pings_counter) + ": " + str(round_trip_time) + "ms")
        rrt_counter += round_trip_time
    except socket.timeout:
        print(str(pings_counter) + ": " + 'timeout')
        timeouts_counter += 1
    pings_counter += 1
    total_pings_sent += 1
    time.sleep(0.1)

print("AVG=" + str(rrt_counter / total_pings_sent) + " TIMEOUTS=" + str(timeouts_counter))
