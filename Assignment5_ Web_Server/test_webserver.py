from socket import *

serverPort = 80
serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print 'the web server is up on port:', serverPort
# Fill in end
while True:
    # Establish the connection
    print 'Ready to serve...'
    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024)
        # print message, '::', message.split()[0], ':', message.split()[1]
        http_method = message.split()[0]
        if http_method != 'GET':
            connectionSocket.send('\nHTTP/1.1 405 status code (Method Not Allowed).\n\n')
            connectionSocket.close()
        else:
            filename = message.split()[1]
            # print filename, '||', filename[1:]
            print filename[1:]

            try:
                # f = open(filename[1:])
                f = open("helloworld.html")

                outputdata = f.read()
                # Send one HTTP header line into socket
                # Fill in start
                connectionSocket.send('\nHTTP/1.1 200 OK\n\n')
                connectionSocket.send(outputdata)
                # Fill in end
                # Send the content of the requested file to the client
                # for i in range(0, len(outputdata)):
                #     connectionSocket.send(outputdata[i])
                connectionSocket.close()
            except:
                print("File not found sent!")
                connectionSocket.send('\nHTTP/1.1 404 Not Found\n\n')
    except IOError:
        # Send response message for file not found
        # Fill in start
        connectionSocket.send('\nHTTP/1.1 404 Not Found\n\n')
