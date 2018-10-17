import socket


def handle_pongs():
    while True:
        try:
            ping_message, ping_server_address = pong_socket.recvfrom(1024)
            print(ping_message, ping_server_address)
            pongNr = ping_message.split("-")[1]
            pong_message = "PONG-" + pongNr
            pong_socket.sendto(pong_message, ping_server_address)
        except:
            pass


address = "localhost"
port = 2000
pong_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pong_socket.setblocking(0)
pong_socket.bind((address, port))

try:
    handle_pongs()
except KeyboardInterrupt:
    pong_socket.close()
