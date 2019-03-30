"""Client.py
Client to connect to the monodrive simulator.
"""
import socket


class Client:
    """Client to connect to the monodrive simulator"""

    def __init__(self, ip, port):
        """ Constructor.

        Args:
            ip(str):  The IP address of the simulator
            port(str): The port for the simulator
        """
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        """ Establish a connection with the server.

        Returns:
            True if the connection was established.
        """
        self.connected = self.sock.connect((self.ip, self.port))
        return self.connected

    def disconnect(self):
        """Disconnect from the server."""
        self.sock.close()

    def read(self, length):
        """Read data from the server.

        Args:
            length(int): The length, in bytes, of data to read

        Returns:
            The binary data that was read from the server.
        """
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
        """Write data to the server.

        Args:
            message(bytearray): The binary message to write to the server

        """
        self.sock.sendall(message)
