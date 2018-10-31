BUFFER_SIZE = 5
filehandle = open("index.txt")
file_content = filehandle.read(BUFFER_SIZE)
print(file_content)

while (file_content):
    file_content = filehandle.read(BUFFER_SIZE)
    print(file_content)
    print(len(file_content))
if not file_content:
    filehandle.close()
