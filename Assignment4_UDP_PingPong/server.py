import socket
import threading

host = 'localhost'
port = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
s.setblocking(0)
s.bind((host, port))

while True:
    data, addr = s.recvfrom(1024)  # buffer size is 1024 bytes
    print(addr)
    print "C:" + data
    datanr = (data.split("-"))[1]
    msgToSend = "PONG-" + datanr
    # print "S:" + msgToSend
    s.sendto(msgToSend, (addr))
    print("SENT!")
    # PING- 29


def start_ponging(self):
    self.is_ponging = True


def do_pong():
    while s.is_ponging:
        try:
            pingMessage, pingerAddress = s.socket.recvfrom(1)
            pongMessage = "p"
            s.socket.sendto("p", pingerAddress)
        except:
            pass


self.pongThread = threading.Thread(target=do_pong, args=())
self.pongThread.start()


def stop_ponging(self):
    self.is_ponging = False


def close(self):
    self.socket.close()
    self.pongThread.join()


s.start_ponging()
print "Ready to receive pings"

# while True:
#     command = raw_input("(quit to stop server)> ")
#     if command == "quit":
#         pongSocket.stop_ponging()
#         pongSocket.close()
#         break
