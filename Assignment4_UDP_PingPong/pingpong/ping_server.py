import socket


def is_valid_ping_format(ping_message):
    valid_ping = True
    if "PING-" == ping_message[:5] and ping_message[len(ping_message) - 1] == "!":
        is_digit = True
        digit_counter = 0
        digit_part = ping_message[5:len(ping_message) - 1]
        while is_digit and digit_counter < len(digit_part) - 1:
            if digit_part[digit_counter].isdigit():
                pass
            else:
                is_digit = False
                break
            digit_counter += 1
        if not is_digit:
            valid_ping = False
    else:
        valid_ping = False
    return valid_ping


def handle_pongs():
    while True:
        try:
            ping_message, ping_server_address = pong_socket.recvfrom(1024)
            # print(ping_message, ping_server_address)
            if is_valid_ping_format(ping_message):
                pongNr = ping_message.split("-")[1].replace("!", "")
                pong_message = "PONG-" + str(pongNr) + "!"
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
