import socket, sys
import thread

try:
    port = 53
except KeyboardInterrupt:
    sys.exit()

buffer_size = 8192


def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('localhost', port))
        # s.listen(5)
    except Exception, e:
        print(e)
        sys.exit(2)
    while True:
        try:
            # conn, addr = s.accept()
            data, addr = s.recvfrom(8192)
            print(data)
            thread.start_new_thread(conn_string, (s, data, addr))
        except KeyboardInterrupt:
            s.close()
            sys.exit(1)
    s.close()


def conn_string(conn, data, addr):
    # print("data:", data)
    try:
        first_line = data.split('\n')[0]

        url = first_line.split(' ')[1]

        http_pos = url.find("://")

        if http_pos == 1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(":")

        webserver_pos = temp.find("/")

        if webserver_pos == -1:
            webserver_pos == len(temp)
        webserver = ""
        req_port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            req_port = 80
            webserver = temp[:webserver_pos]
        else:
            req_port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        proxy_server(webserver, req_port, conn, addr, data)
    except Exception, e:
        pass


def proxy_server(webserver, port, conn, addr, data):
    print("data:", data)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((webserver, port))
        s.send(data)

        while True:
            reply = s.recv(8192)

            if len(reply) > 0:
                conn.send(reply)

                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
            else:
                break
        s.close()
        conn.close()
    except socket.error, (value, msg):
        s.close()
        conn.close()
        sys.exit(1)


start()
