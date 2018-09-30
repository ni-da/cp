from __future__ import print_function

__author__ = 'Bram, Maarten Wijnants'
import sys
import socket
from threading import Thread

# !/usr/bin/python

"""
Please realize that this is proof-of-concept code and that it does not give
examples of good coding practices. Make sure that your solution caters to the
original assignment, and *not* to this code.
"""

print_server_data_thread_running = True
print_server_data_thread_timeout = 1


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen. Stolen from http://code.activestate.com/recipes/134892/"""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            # self.impl = _GetchUnix()
            print("Not working on Windows")

    def __call__(self):
        return self.impl()


# class _GetchUnix:
#     def __init__(self):
#         import tty, sys
#
#     def __call__(self):
#         import sys, tty, termios
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)
#         try:
#             tty.setraw(sys.stdin.fileno())
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#         return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def print_server_data_thread(sock):
    sock.settimeout(print_server_data_thread_timeout)
    global print_server_data_thread_running

    while print_server_data_thread_running:
        try:
            data = sock.recv(1024)
            if data == "":
                print("\nSERVER CLOSED YOUR CONNECTION")
                break
            else:
                print("\nSERVER: %s\r\n" % data.strip(), end="")
        except socket.timeout:
            continue
        except socket.error, e:
            err = e.args[0]
            print("\nERROR: Server problem: %s" % e)
            break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: run with argument PORT (e.g. %s 2000)" % sys.argv[0])
        exit(1)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(('localhost', int(sys.argv[1])))
    server_data_thread = Thread(target=print_server_data_thread, args=(server,))
    server_data_thread.start()
    while True:
        c = getch()
        if c == '':
            break
        if c == '\r':
            c = '\n'
        server.send(c)
        print(c, end='')

    # On exit
    print("\nExiting...")
    print_server_data_thread_running = False
    server_data_thread.join(print_server_data_thread_timeout + 1)
    server.close()
