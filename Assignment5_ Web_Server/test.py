import socket
import datetime
import sys


def close_server(conn, s):
    conn.close
    s.close
    sys.exit()


def get_fileType(filenamestr):
    allowed_types = ["html", "jpg", "png", "js", "css", "zip"]
    if "." in filenamestr:
        filetype = filenamestr.split(".")[1]
        if filetype in allowed_types:
            return filetype
        else:
            return "Nok"
    else:
        if filenamestr[:-1] != "/":
            filenamestr += "/"
        return filenamestr + "index.html"


# Content-Type: application/json
def get_ContentType(filetype):
    allowed_types = ["html", "jpg", "png", "js", "css", "zip"]
    content_types = ["text/html", "image/jpg", "image/png", "text/css", "application/javascript", "application/zip"]
    filetype_code = allowed_types.index(filetype)
    return content_types[filetype_code]


def get_error_response(response_msg):
    header = '\nHTTP/1.1 ' + response_msg + '\n\n'
    response = '<html><body><center><h3>Error: ' + response_msg + '</h3></center></body></html>'.encode(
        'utf-8')
    final_response = header.encode('utf-8')
    final_response += response
    return final_response


host = 'localhost'
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

s.listen(1)
while 1:
    conn, addr = s.accept()
    cliAdr, cliPort = addr

    message = conn.recv(1024)
    print(message)
    http_method = message[:3]
    if http_method != 'GET':
        conn.sendall(get_error_response("405 Method Not Allowed"))
        conn.close()

    else:
        filename = message.split()[1]
        filename = filename[1:]
        if get_fileType(filename) != "Nok":
            if "index.html" in get_fileType(filename):
                filename = get_fileType(filename)
                print(filename)
            content_type = get_ContentType(get_fileType(filename))
            try:
                filehandle = open(filename)
                file_content = filehandle.read()
                filehandle.close()
                print(file_content)

                # conn.send('HTTP/1.1 200 OK\n')
                header = 'HTTP/1.1 200 OK\n'
                header += 'Date: {now}\n'.format(now=datetime.datetime.now())
                header += 'Content-Type: ' + str(content_type) + '\n\n'
                # conn.send('Content-Type: ' + content_type + '\n\n')
                final_response = header.encode('utf-8')
                final_response += file_content
                conn.sendall(final_response)

                # conn.send(file_content)
            except:
                conn.sendall(get_error_response("404 Not Found"))
        else:
            conn.sendall(get_error_response("415 Unsupported Media Type"))

conn.close()
s.close()
