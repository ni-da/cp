from socket import *
import sys
import threading


class PongSocket:
    def __init__(self, address, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setblocking(0)
        self.socket.bind((address, port))

    def start_ponging(self):
        self.is_ponging = True

        def do_pong():
            while self.is_ponging:
                try:
                    pingMessage, pingerAddress = self.socket.recvfrom(1024)
                    print(pingMessage, pingerAddress)
                    pongNr = pingMessage.split("-")[1]
                    pongMessage = "PONG-" + pongNr
                    self.socket.sendto(pongMessage, pingerAddress)
                except:
                    pass

        self.pongThread = threading.Thread(target=do_pong, args=())
        self.pongThread.start()

    def stop_ponging(self):
        self.is_ponging = False

    def close(self):
        self.socket.close()
        self.pongThread.join()


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print "Usage:"
    #     print ""
    #     print "    python Server.py $address $port"
    #     print "    $address - bind address"
    #     print "    $port    - bind port"
    #     sys.exit(1)

    address = "localhost"
    port = 2000
    pongSocket = PongSocket(address, port)
    pongSocket.start_ponging()
    print "Ready to receive pings"
    while True:
        command = raw_input("(quit to stop server)> ")
        if command == "quit":
            pongSocket.stop_ponging()
            pongSocket.close()
            break
