import socket

HOST = ''    # The remote host
PORT = 6666              # The same port as used by the server
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    data = input()
    print('Sending {}'.format(data))
    s.sendall(data.encode())
    s.close()
