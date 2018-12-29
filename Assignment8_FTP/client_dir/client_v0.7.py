import socket, string, sys


class FTPclient:
    def __init__(self, address, port, data_port, username, password):
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = int(port)
        self.data_port = int(data_port)
        self.username = username
        self.password = password
        self.valid_commands = ['ls', 'put', 'get', 'del', 'bye']
        self.commands_to_send = ['NLST', 'STOR', 'RETR', 'DELE', 'QUIT']
        self.next_data_port = 0

    def create_connection(self):
        try:
            server_address = (self.address, self.port)
            self.control_sock.connect(server_address)
            sys.stdout.write('Connected to ' + str(self.address) + ':' + str(self.port) + '\n')
            sys.stdout.flush()
            server_msg = self.control_sock.recv(1024)
            if server_msg[:3] == '220':  # Service ready for new user.
                self.control_sock.sendall('USER ' + self.username + '\r\n')
                server_msg = self.control_sock.recv(1024)
                if server_msg[:3] == '331':  # User name okay, need password.
                    self.control_sock.sendall('PASS ' + self.password + '\r\n')
                    server_msg = self.control_sock.recv(1024)
                    if server_msg[:3] == '230':  # User logged in, proceed. Logged out if appropriate.
                        pass
        except KeyboardInterrupt:
            self.close_client()
        except:
            sys.stdout.write('Connection to{0}:{1}failed'.format(str(self.address), str(self.port)))
            sys.stdout.flush()

            self.close_client()

    def start(self):
        try:
            self.create_connection()
        except Exception, e:
            self.close_client()

        while True:
            try:
                # command = raw_input('Enter command: ')
                # print('cmd:')
                command = sys.stdin.readline()
                command = command[:len(command)-1]
                if not command:
                    sys.stdout.write('Need a command!\r\n')
                    sys.stdout.flush()
                    continue
            except KeyboardInterrupt:
                self.close_client()
            if command[:3] in self.valid_commands or command == "ls":
                cmd_index = self.valid_commands.index(command[:3])
                new_cmd = self.commands_to_send[cmd_index]
                if new_cmd == 'QUIT':
                    self.control_sock.sendall(new_cmd + '\r\n')
                    sys.stdout.write(str(self.control_sock.recv(1024)) + '\n')
                    sys.stdout.flush()
                    self.close_client()
                else:
                    if new_cmd == 'NLST':
                        filename = 'test'
                    else:
                        filename = command.split(' ')[1]
                    func = getattr(self, new_cmd)
                    res = func(filename)
                    if res == 'error': pass
                    else:
                        res_by_serv = self.control_sock.recv(1024)
                        if '226' in res_by_serv or '250' in res_by_serv:
                            sys.stdout.write('Command completed!\n')
                            sys.stdout.flush()
                        else:
                            sys.stdout.write(str(res_by_serv) + '\n')
                            sys.stdout.flush()
            else:
                sys.stdout.write('Command not supported\n')
                sys.stdout.flush()

    def connect_datasock(self):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        datasock_host, datasock_port = self.control_sock.getsockname()
        datasock_port += 1

        if self.next_data_port == 0:
            self.next_data_port = datasock_port + 1
        else:
            datasock_port = self.next_data_port
            self.next_data_port += 1

        self.data_socket.bind((datasock_host,
                               datasock_port))
        self.data_socket.listen(1)
        hbytes = string.splitfields(datasock_host, '.')
        bytes = hbytes + [str(0)] + [str(datasock_port)]
        port_cmd = 'PORT ' + string.joinfields(bytes, ',')
        self.control_sock.send(port_cmd + '\r\n')
        srv_msg = self.control_sock.recv(1024)
        return (srv_msg)

    def NLST(self, filename):
        try:
            data_connection = self.connect_datasock()
            if '200' in data_connection:  # The requested action has been successfully completed.
                self.control_sock.send('NLST\r\n')
                srv_msg = self.control_sock.recv(1024)
                if '150' in srv_msg:  # File status okay; about to open data connection.
                    ftp_server_conn, ftp_server_addr = self.data_socket.accept()
                    while True:
                        data_from_ftp_serv = ftp_server_conn.recv(1024)
                        sys.stdout.write(str(data_from_ftp_serv) + '\n')
                        sys.stdout.flush()
                        if not data_from_ftp_serv: break
                    ftp_server_conn.close()
            else:
                sys.stdout.write('Connection for data failed' + str(data_connection) + '\n')
                sys.stdout.flush()

        except Exception, e:
            sys.stdout.write(str(e) + '\n')
            sys.stdout.flush()
        finally:
            self.data_socket.close()

    def STOR(self, filename):
        try:
            data_connection = self.connect_datasock()
            if '200' in data_connection:  # The requested action has been successfully completed.
                self.control_sock.send('STOR ' + filename + '\r\n')
                srv_msg = self.control_sock.recv(1024)
                if '150' in srv_msg:  # File status okay; about to open data connection.
                    ftp_server_conn, ftp_server_addr = self.data_socket.accept()  # self.connect_datasock()
                    try:
                        f = open(filename, 'r')
                        upload = f.read(1024)
                    except Exception, e:
                        sys.stdout.write('File to upload not found!\r\n')
                        sys.stdout.flush()
                        return
                    while upload:
                        ftp_server_conn.send(upload)
                        upload = f.read(1024)
                        if not upload:
                            f.close()
                    ftp_server_conn.close()
            else:
                sys.stdout.write('Connection for data failed' + str(data_connection) + '\r\n')
                sys.stdout.flush()

        except Exception, e:
            sys.stdout.write(str(e) + '\r\n')
            sys.stdout.flush()

        finally:
            self.data_socket.close()

    def RETR(self, filename):
        try:
            data_connection = self.connect_datasock()
            if '200' in data_connection:  # The requested action has been successfully completed.
                self.control_sock.send('RETR ' + filename + '\r\n')
                srv_msg = self.control_sock.recv(1024)
                if '150' in srv_msg:  # File status okay; about to open data connection.
                    ftp_server_conn, ftp_server_addr = self.data_socket.accept()
                    while True:
                        download = ftp_server_conn.recv(1024)
                        try:
                            f = open('downloads/' + filename, 'w')
                            f.write(download)
                            if not download: break
                        except Exception, e:
                            sys.stdout.write(str(e) + '\n')
                            sys.stdout.flush()
                            f.close()
                    ftp_server_conn.close()
                elif '550' in srv_msg:  # Can't open : No such file or directory
                    sys.stdout.write('REQUESTED FILE UNAVAILABLE' + '\n')
                    sys.stdout.flush()
                    return 'error'
            else:
                sys.stdout.write('Connection for data failed' + str(data_connection) + '\n')
                sys.stdout.flush()
        except Exception, e:
            sys.stdout.write(str(e) + '\n')
            sys.stdout.flush()
        finally:
            self.data_socket.close()

    def DELE(self, filename):
        self.control_sock.send('DELE ' + filename + '\r\n')

    # stop FTP client, close the connection and exit the program
    def close_client(self):
        sys.stdout.write('Closing socket connection...' + '\n')
        sys.stdout.flush()
        self.control_sock.close()
        sys.stdout.write('FTP client terminating...' + '\n')
        sys.stdout.flush()
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
