import socket


class Client:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        print("connecting to {0}:{1}".format(self.ip, self.port))
        self.sock.connect((self.ip, self.port))

    def disconnect(self):
        self.sock.close()

    def read(self, length):
        data = b''
        count = 0
        while count < length:
            b = self.sock.recv(length - count)
            if not b or len(b) == 0:
                break

            data = data + b
            count = count + len(b)

        return data

    def write(self, message):
        self.sock.sendall(message)
