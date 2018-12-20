import socket
import datetime

0
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


def handle_request(conn, addr):
    BUFFER_SIZE = 1024
    cliAdr, cliPort = addr
    message = conn.recv(1024)
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
            content_type = get_ContentType(get_fileType(filename))
            try:
                filehandle = open(filename)

                header = 'HTTP/1.1 200 OK\n'
                header += 'Date: {now}\n'.format(now=datetime.datetime.now())
                header += 'Connection: close\n'
                header += 'Content-Type: ' + str(content_type) + '\n\n'
                final_response_header = header.encode('utf-8')
                conn.send(final_response_header)

                file_content = filehandle.read(BUFFER_SIZE)
                while (file_content):
                    conn.sendall(file_content)
                    file_content = filehandle.read(BUFFER_SIZE)

                if not file_content:
                    filehandle.close()
                    conn.close()
            except:
                conn.sendall(get_error_response("404 Not Found"))
        else:
            conn.sendall(get_error_response("415 Unsupported Media Type"))


host = 'localhost'
port = 8080
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
except:
    print("Some problem!")
threads = []
while 1:
    s.listen(5)
    conn, addr = s.accept()
    newThread = handle_request(conn, addr)
    threads.append(newThread)
for t in threads:
    t.join()

# conn.close()
# s.close()
