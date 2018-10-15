import socket
from threading import Thread
import time

host = 'localhost'
port = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def send_dgrams(amount=5):
    for i in range(1, amount + 1):
        MESSAGE = "PING-" + str(i)
        # wait 0.1 sec -> 100 msc
        s.sendto(MESSAGE, (host, port))
        # start timer



# def recv_replies():
#     data = s.recv(1024)
#     print(data)
#
#
# sending_thread = Thread(target=send_dgrams, args=())
# sending_thread.start()
#
# recv_thread = Thread(target=recv_replies, args=())
# time.sleep(0.1)
# recv_thread.start()

# time counter
# thread sending dgrams
# thread recieving dgrams
