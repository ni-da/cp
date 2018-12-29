import socket
import sys


class FTPclient:
    def __init__(self, address, port, data_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = int(port)
        self.data_port = int(data_port)

    def create_connection(self):
        try:
            server_address = (self.address, self.port)
            self.sock.connect(server_address)
            print 'Connected to', self.address, ':', self.port
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


            server_data = self.sock.recv(1024)
            print(server_data)


        # while server_data[0:3] != "230":
        #     print(server_data)
        #     user_cred = raw_input('Enter username and password: ')
        #     self.sock.send(user_cred)
        #     server_data = self.sock.recv(1024)
        # print(server_data)

        while True:
            try:
                command = raw_input('Enter command: ')
                if not command:
                    print 'Need a command.'
                    continue
            except KeyboardInterrupt:
                self.close_client()
            cmd = command[:4].strip()
            path = command[4:].strip()
            try:
                self.sock.send(command)
                data = self.sock.recv(1024)
                print data
                if cmd == 'bye':
                    self.close_client()
                elif cmd == 'ls' or cmd == 'put' or cmd == 'get':
                    if data and (data[0:3] == '125'):
                        func = getattr(self, cmd)
                        func(path)
                        data = self.sock.recv(1024)
                        print data
            except Exception, e:
                print str(e)
                self.close_client()

    def connect_datasock(self):
        self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.datasock.connect((self.address, self.data_port))

    def ls(self, path):
        try:
            self.connect_datasock()
            while True:
                dirlist = self.datasock.recv(1024)
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

    # stop FTP client, close the connection and exit the program
    def close_client(self):
        print 'Closing socket connection...'
        self.sock.close()

        print 'FTP client terminating...'
        quit()


address = 'ftp.dlptest.com'
port = 21
data_port = 20

ftpClient = FTPclient(address, port, data_port)
ftpClient.start()
