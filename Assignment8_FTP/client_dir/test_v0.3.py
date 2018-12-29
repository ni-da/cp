# A simple FTP client.
#
# The information to write this program was gathered from RFC 959,
# but this is not a complete implementation!  Yet it shows how a simple
# FTP client can be built, and you are welcome to extend it to suit
# it to your needs...
#
# How it works (assuming you've read the RFC):
#
# User commands are passed uninterpreted to the server.  However, the
# user never needs to send a PORT command.  Rather, the client opens a
# port right away and sends the appropriate PORT command to the server.
# When a response code 150 is received, this port is used to receive
# the data (which is written to stdout in this version), and when the
# data is exhausted, a new port is opened and a corresponding PORT
# command sent.  In order to avoid errors when reusing ports quickly
# (and because there is no s.getsockname() method in Python yet) we
# cycle through a number of ports in the 50000 range.


import sys, string
from socket import *


BUFSIZE = 1024

# Default port numbers used by the FTP protocol.
FTP_PORT = 21
FTP_DATA_PORT = FTP_PORT - 1

# Change the data port to something not needing root permissions.
FTP_DATA_PORT = FTP_DATA_PORT + 50000


# Main program (called at the end of this file).
def main():
    hostname = "ftp.dlptest.com" #sys.argv[1]
    control(hostname)


# Control process (user interface and user protocol interpreter).
#


# stop FTP client, close the connection and exit the program
def close_client():
    print 'Closing socket connection...'
    control_sock.close()
    print 'FTP client terminating...'
    quit()

def create_conn():
    try:
        server_address = (hostname, FTP_PORT)
        control_sock.connect(server_address)
        print 'Connected to', hostname, ':', FTP_PORT
        server_msg = control_sock.recv(1024)

        # print(server_msg)
        if server_msg[:3] == '220':  # Service ready for new user.
            print(server_msg)
            control_sock.sendall('USER ' + username + '\r\n')
            server_msg = control_sock.recv(1024)
            if server_msg[:3] == '331':  # User name okay, need password.
                print(server_msg)
                control_sock.sendall('PASS ' + password + '\r\n')
                server_msg = control_sock.recv(1024)
                if server_msg[:3] == '230':  # User logged in, proceed. Logged out if appropriate.
                    control_sock.sendall('PASV\r\n')
                    server_msg = (control_sock.recv(1024))


    except KeyboardInterrupt:
        close_client()
    except:
        print 'Connection to', hostname, ':', FTP_PORT, 'failed'
        close_client()


def control(hostname):
    create_conn()
    #
    # Create control connection
    #
    # s = socket(AF_INET, SOCK_STREAM)
    # s.connect((hostname, FTP_PORT))

    f = control_sock.makefile('r') # Reading the replies is easier from a file...
    #
    # Control loop
    #
    r = None
    while 1:
        cmd = getcommand()
        print("CMD:", cmd)
        if not cmd: break
        # s.send(cmd + '\r\n')
        control_sock.send(cmd + '\r\n')
        code = getreply(f)
        print("Code: "+code)
        # if '220' in code:
        #     s.sendall('USER dlpuser@dlptest.com\r\n')
        #     s.sendall('PASS e73jzTRTNqCN9PYAAjjn\r\n')
        #     response_username = s.recv(BUFSIZE)
        #     print(response_username)
        #     # if '331' in code:
        #     #     s.sendall('PASS e73jzTRTNqCN9PYAAjjn\r\n')
        #     #     response_pass = s.recv(BUFSIZE)
        #     #     print("At pass", response_pass)
        # if '230' in code:
        #     response_username = s.recv(BUFSIZE)
        #     print(response_username)
        if '500' in code:
            print('Syntax error')
        if code in ('221', 'EOF'): break
        if code == '150': #File status okay; about to open data connection.
            getdata(r)
            code = getreply(f)
            r = None
        if not r:
            r = newdataport(control_sock, f)



# Create a new data port and send a PORT command to the server for it.
# (Cycle through a number of ports to avoid problems with reusing
# a port within a short time.)
#
nextport = 0
#
def newdataport(s, f):
    global nextport
    port = nextport + FTP_DATA_PORT
    nextport = (nextport+1) % 16
    r = socket(AF_INET, SOCK_STREAM)
    r.bind((gethostbyname(gethostname()), port))
    r.listen(1)
    sendportcmd(s, f, port)
    return r


# Send an appropriate port command.
#
def sendportcmd(s, f, port):
    hostname = gethostname()
    hostaddr = gethostbyname(hostname)
    hbytes = string.splitfields(hostaddr, '.')
    pbytes = [repr(port//256), repr(port%256)]
    bytes = hbytes + pbytes
    cmd = 'PORT ' + string.joinfields(bytes, ',')
    s.send(cmd + '\r\n')
    code = getreply(f)


# Process an ftp reply and return the 3-digit reply code (as a string).
# The reply should be a line of text starting with a 3-digit number.
# If the 4th char is '-', it is a multi-line reply and is
# terminate by a line starting with the same 3-digit number.
# Any text while receiving the reply is echoed to the file.
#
def getreply(f):
    print("SOME", f)
    line = f.readline()
    print("LINE", line)
    if not line: return 'EOF'
    print line,
    code = line[:3]
    if line[3:4] == '-':
        while 1:
            line = f.readline()
            if not line: break # Really an error
            print line,
            if line[:3] == code and line[3:4] != '-': break
    return code


# Get the data from the data connection.
#
def getdata(r):
    print '(accepting data connection)'
    conn, host = r.accept()
    print '(data connection accepted)'
    while 1:
        data = conn.recv(BUFSIZE)
        if not data: break
        sys.stdout.write(data)
    print '(end of data connection)'

# Get a command from the user.
#
def getcommand():
    try:
        while 1:
            line = raw_input('ftp.py> ')
            if line: return line
    except EOFError:
        return ''


# Call the main program.
#
# main()
hostname = "ftp.dlptest.com" #sys.argv[1]
username = "dlpuser@dlptest.com"
password = "e73jzTRTNqCN9PYAAjjn"
control_sock = socket(AF_INET, SOCK_STREAM)
control(hostname)
