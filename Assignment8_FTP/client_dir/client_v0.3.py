import socket, string
import sys

FTP_DATA_PORT = 20 + 50000
nextport = 0

def sendportcmd(s,port):
    hostname = socket.gethostname()
    print("HOSTNAME", hostname)
    hostaddr = socket.gethostbyname(hostname)
    print("hostaddr", hostaddr)
    hbytes = string.splitfields(hostaddr, '.')
    print("hbytes", hbytes)
    pbytes = [repr(port//256), repr(port%256)]
    print("pbytes", pbytes)
    bytes = hbytes + pbytes
    cmd = 'PORT ' + string.joinfields(bytes, ',')
    print("CMD", cmd)
    s.send(cmd + '\r\n')
    # code = socket.getreply(f)
    srv_msg = s.recv(1024)
    print(srv_msg)

def newdataport(s):
    global nextport
    port = nextport + FTP_DATA_PORT
    nextport = (nextport+1) % 16
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.bind((socket.gethostbyname(socket.gethostname()), port))
    r.listen(1)
    sendportcmd(s, port)
    return r

class FTPclient:
    def __init__(self, address, port, data_port, username, password):
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = int(port)
        self.data_port = int(data_port)
        self.username = username
        self.password = password
        self.valid_commands = ['ls', 'put', 'get', 'del', 'bye']
        self.commands_to_send = ['NLST', 'STOR', 'RETR', 'DELE ', 'QUIT']

    # def newdataport(self):
    #     FTP_DATA_PORT = 20 + 50000
    #     client_data_port = FTP_DATA_PORT
    #     self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.data_port =
    def create_connection(self):
        try:
            server_address = (self.address, self.port)
            self.control_sock.connect(server_address)
            # print("SOCK: ", self.control_sock.getsockname())
            print 'Connected to', self.address, ':', self.port
            server_msg = self.control_sock.recv(1024)
            # print(server_msg)
            if server_msg[:3] == '220':  # Service ready for new user.
                print(server_msg)
                self.control_sock.sendall('USER ' + self.username + '\r\n')
                server_msg = self.control_sock.recv(1024)
                if server_msg[:3] == '331':  # User name okay, need password.
                    print(server_msg)
                    self.control_sock.sendall('PASS ' + self.password + '\r\n')
                    server_msg = self.control_sock.recv(1024)
                    if server_msg[:3] == '230':  # User logged in, proceed. Logged out if appropriate.
                        pass
                        # data = server_msg
            # new data port
            # self.control_sock.sendall('NLST' + '\r\n')
            # print(self.control_sock.recv(1024))

            #         else:
            #             print 'Connection to', self.address, ':', self.port, 'failed'
            #             print(server_msg)
            #             self.close_client()
            #     else:
            #         print 'Connection to', self.address, ':', self.port, 'failed'
            #         print(server_msg)
            #         self.close_client()
            # else:
            #     print 'Connection to', self.address, ':', self.port, 'failed'
            #     print(server_msg)
            #     self.close_client()
        except KeyboardInterrupt:
            self.close_client()
        except:
            print 'Connection to', self.address, ':', self.port, 'failed'
            self.close_client()

    def start(self):
        try:
            self.create_connection()
        except Exception, e:
            self.close_client()

        while True:
            try:
                command = raw_input('Enter command: ')
                if not command:
                    print 'Need a command.'
                    continue
            except KeyboardInterrupt:
                self.close_client()

            if command[:4] in self.valid_commands or command == "bye":
                cmd_index = self.valid_commands.index(command)
                command = self.commands_to_send[cmd_index]

                cmd = command[:4].strip()
                path = command[4:].strip()
                # try:
                    # self.control_sock.sendall(command + '\r\n')
                    # data = self.control_sock.recv(1024)
                    # print(data)
                    # print(data, cmd)
                if cmd == 'QUIT':
                    self.control_sock.sendall(cmd + '\r\n')
                    print(self.control_sock.recv(1024))
                    self.close_client()
                elif cmd == 'NLST' or cmd == 'STOR' or cmd == 'RETR':
                    # self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # datasock_host, datasock_port = self.control_sock.getsockname()
                    # datasock_port += 1
                    # self.data_socket.bind((datasock_host,
                    #                        datasock_port))
                    # self.data_socket.listen(1)
                    # hbytes = string.splitfields(datasock_host, '.')
                    # bytes = hbytes +[str(0)]+ [str(datasock_port)]
                    # port_cmd = 'PORT ' + string.joinfields(bytes, ',')
                    # print("CMD", port_cmd)
                    # self.control_sock.send(port_cmd + '\r\n')
                    # srv_msg = self.control_sock.recv(1024)
                    # print(srv_msg)
                    # self.control_sock.send('NLST\r\n')
                    # srv_msg = self.control_sock.recv(1024)
                    # print(srv_msg)
                    # if '150' in srv_msg:
                    #     ftp_server_conn, ftp_server_addr = self.data_socket.accept()
                    #     while True:
                    #         data_from_ftp_serv = ftp_server_conn.recv(1024)
                    #         print(data_from_ftp_serv)
                    #         if not data_from_ftp_serv:
                    #             print('Got all data')
                    #             break
                    #     ftp_server_conn.close()
                    if cmd == 'NLST': self._NLST()

            else:
                print('Command not supported')

    def connect_datasock(self):
        self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.datasock.connect((self.address, self.data_port))
        return self.datasock.getsockname()


    def _NLST(self):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        datasock_host, datasock_port = self.control_sock.getsockname()
        datasock_port += 1
        self.data_socket.bind((datasock_host,
                               datasock_port))
        self.data_socket.listen(1)
        hbytes = string.splitfields(datasock_host, '.')
        bytes = hbytes + [str(0)] + [str(datasock_port)]
        port_cmd = 'PORT ' + string.joinfields(bytes, ',')
        print("CMD", port_cmd)
        self.control_sock.send(port_cmd + '\r\n')
        srv_msg = self.control_sock.recv(1024)
        print(srv_msg)
        self.control_sock.send('NLST\r\n')
        srv_msg = self.control_sock.recv(1024)
        print(srv_msg)
        if '150' in srv_msg:
            ftp_server_conn, ftp_server_addr = self.data_socket.accept()
            while True:
                data_from_ftp_serv = ftp_server_conn.recv(1024)
                print(data_from_ftp_serv)
                if not data_from_ftp_serv:
                    print('Got all data')
                    break
            ftp_server_conn.close()

    def NLST(self, path):
        print("NLST")
        try:
            # self.connect_datasock()
            # self.datasock.sendall('NLST\r\n')
            while True:
                dirlist = self.data_socket.recv(1024)
                if not dirlist: break
                sys.stdout.write(dirlist)
                sys.stdout.flush()
        except Exception, e:
            print str(e)
        finally:
            self.datasock.close()

    def put(self, path):
        try:
            self.connect_datasock()
            f = open(path, 'r')
            upload = f.read(1024)
            while upload:
                self.datasock.send(upload)
                upload = f.read(1024)
        except Exception, e:
            print str(e)
        finally:
            f.close()
            self.datasock.close()

    def get(self, path):
        try:
            self.connect_datasock()
            download = self.datasock.recv(1024)
            if "filename:" in download:
                filename = download[len("filename:") + 1:]
                f = open(filename, 'w')
            while True:
                download = self.datasock.recv(1024)
                print(download)
                if not download: break
                f.write(download)
        except Exception, e:
            print str(e)
        finally:
            f.close()
            self.datasock.close()

    def DELE(self, path):
        pass

    # stop FTP client, close the connection and exit the program
    def close_client(self):
        print 'Closing socket connection...'
        self.control_sock.close()

        print 'FTP client terminating...'
        quit()


if ':' in sys.argv[1]:
    port = sys.argv[1].split(':')[1]
    host = sys.argv[1].split(':')[0]
else:
    port = 21
    host = sys.argv[1]
data_port = 20
username = sys.argv[2]
password = sys.argv[3]

ftpClient = FTPclient(host, port, data_port, username, password)
ftpClient.start()
