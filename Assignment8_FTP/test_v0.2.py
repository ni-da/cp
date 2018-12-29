import socket
import os
import sys
import threading
import time


class FTPThreadServer(threading.Thread):
    def __init__(self, (client, client_address), local_ip, data_port):
        self.client = client
        self.client_address = client_address
        self.cwd = os.getcwd()
        self.data_address = (local_ip, data_port)

        threading.Thread.__init__(self)

    def check_user_cred(self, param):
        try:
            cli_username = param.split(',')[0]
            cli_pass = param.split(',')[1]
            if username == cli_username and password == cli_pass:
                return True
            return False
        except:
            return False

    def start_datasock(self):
        try:
            print 'Creating data socket on' + str(self.data_address)

            # create TCP for data socket
            self.datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.datasock.bind(self.data_address)
            self.datasock.listen(5)

            print 'Data socket is started. Listening to' + str(self.data_address) + '...'
            self.client.send('125 Data connection already open; transfer starting.\r\n')

            return self.datasock.accept()
        except Exception, e:
            print 'ERROR: test ' + str(self.client_address) + ': ' + str(e)
            self.close_datasock()
            self.client.send('425 Cannot open data connection.\r\n')

    def close_datasock(self):
        try:
            self.datasock.close()
        except:
            pass

    def run(self):
        try:
            print 'client connected: ' + str(self.client_address) + '\n'
            self.client.send('332 Welcome to FTP server! Give (<username>,<password>)\r\n')
            user_data = self.client.recv(1024)
            while not self.check_user_cred \
                        (user_data):
                self.client.send('332 Welcome to FTP server! Give (<username>,<password>)\r\n')
                user_data = self.client.recv(1024)
            self.client.send('230 User logged in.\r\n')
            while True:
                cmd = self.client.recv(1024)
                if not cmd: break
                if 'del' in cmd: cmd = '_' + cmd
                try:
                    func = getattr(self, cmd[:4].strip())
                    func(cmd)
                except AttributeError, e:
                    print 'ERROR: ' + str(self.client_address) + ': Invalid Command.' + cmd
                    self.client.send('550 Invalid Command\r\n')
        except Exception, e:
            print 'ERROR: ' + str(self.client_address) + ': ' + str(e)
            self.bye('')

    # bye : disconnects from the FTP server and exits the program
    def bye(self, cmd):
        try:
            self.client.send('221 Goodbye.\r\n')
        except:
            pass
        finally:
            print 'Closing connection from ' + str(self.client_address) + '...'
            self.close_datasock()
            self.client.close()
            quit()

    # ls : outputs the list of files that are hosted on the FTP server
    def ls(self, cmd):
        (client_data, client_address) = self.start_datasock()
        try:
            listdir = os.listdir(self.cwd)
            if not len(listdir):
                max_length = 0
            else:
                max_length = len(max(listdir, key=len))

            header = '| %*s | %9s | %12s | %20s | %11s | %12s |' % (
                max_length, 'Name', 'Filetype', 'Filesize', 'Last Modified', 'Permission', 'User/Group')
            table = '%s\n%s\n%s\n' % ('-' * len(header), header, '-' * len(header))
            client_data.send(table)

            for i in listdir:
                path = os.path.join(self.cwd, i)
                stat = os.stat(path)
                data = '| %*s | %9s | %12s | %20s | %11s | %12s |\n' % (
                    max_length, i, 'Directory' if os.path.isdir(path) else 'File', str(stat.st_size) + 'B',
                    time.strftime('%b %d, %Y %H:%M', time.localtime(stat.st_mtime))
                    , oct(stat.st_mode)[-4:], str(stat.st_uid) + '/' + str(stat.st_gid))
                client_data.send(data)

            table = '%s\n' % ('-' * len(header))
            client_data.send(table)

            self.client.send('\r\n226 Directory send OK.\r\n')
        except Exception, e:
            print 'ERROR: ' + str(self.client_address) + ': ' + str(e)
            self.client.send('426 Connection closed; transfer aborted.\r\n')
        finally:
            client_data.close()
            self.close_datasock()

    # del remote_filename : removes a file from the server
    def _del(self, cmd):
        path = cmd[4:].strip()
        filename = os.path.join(self.cwd, path)
        try:
            if not path:
                self.client.send('501 Missing arguments <filename>.\r\n')
            else:
                os.remove(filename)
                self.client.send('250 File deleted: ' + filename + '.\r\n')
        except Exception, e:
            print 'ERROR: ' + str(self.client_address) + ': ' + str(e)
            self.client.send('550 Failed to delete file ' + filename + '.')

    # put local_filename : uploads a file to the FTP server
    def put(self, cmd):
        path = cmd[4:].strip()
        if not path:
            self.client.send('501 Missing arguments <filename>.\r\n')
            return

        fname = os.path.join(self.cwd, path)
        (client_data, client_address) = self.start_datasock()

        try:
            file_write = open(fname, 'w')
            while True:
                data = client_data.recv(1024)
                if not data:
                    break
                file_write.write(data)

            self.client.send('226 Transfer complete.\r\n')
        except Exception, e:
            print 'ERROR: ' + str(self.client_address) + ': ' + str(e)
            self.client.send('425 Error writing file, cannot open data connection. \r\n')
        finally:
            client_data.close()
            self.close_datasock()
            file_write.close()

    # get remote_filename : downloads a file from the server
    def get(self, cmd):
        path = cmd[4:].strip()

        if not path:
            self.client.send('501 Missing arguments <filename>.\r\n')
            return

        fname = os.path.join(self.cwd, path)
        (client_data, client_address) = self.start_datasock()
        if not os.path.isfile(fname):
            self.client.send('550 REQUESTED FILE UNAVAILABLE.\r\n')
        else:
            try:
                client_data.send(('filename: downloads/' + os.path.basename(fname)))
                file_read = open(fname, 'r')
                data = file_read.read(1024)
                while data:
                    client_data.send(data)
                    data = file_read.read(1024)
                self.client.send('226 Transfer complete, closing data connection\r\n')
            except Exception, e:
                print 'ERROR: ' + str(self.client_address) + ': ' + str(e)
                self.client.send('426 Connection closed; transfer aborted.\r\n')
            finally:
                client_data.close()
                self.close_datasock()
                file_read.close()


class FTP_client:
    def __init__(self, host, port, data_port, username, password):
        # server address at localhost
        self.address = host
        self.port = int(port)
        self.data_port = int(data_port)
        self.username = username
        self.password = password

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

    # def start_sock(self):
    #     # create TCP socket
    #     self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     try:
    #         self.sock.connect((self.address, self.port))
    #         # self.sock.bind(server_address)
    #         # self.sock.listen(5)
    #     except Exception, e:
    #         print 'Failed to create server on', self.address, ':', self.port, 'because', str(e.strerror)
    #         quit()

    def start(self):
        try:
            self.create_connection()
        except Exception, e:
            self.close_client()
        server_data = self.sock.recv(1024)

        try:
            while True:
                print 'Waiting for a connection'
                thread = FTPThreadServer(self.sock.accept(), self.address, self.data_port)
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print 'Closing socket connection'
            self.sock.close()
            quit()


# Main
if ':' in sys.argv[1]:
    port = sys.argv[1].split(':')[1]
    host = sys.argv[1].split(':')[0]
else:
    port = 21
    host = sys.argv[1]
data_port = 20
username = sys.argv[2]
password = sys.argv[3]

client = FTP_client(host, port, data_port, username, password)
client.start()
# main(host, port)
