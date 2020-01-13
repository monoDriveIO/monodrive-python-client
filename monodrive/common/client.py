"""client.py
client to connect to the monodrive simulator.
"""
import socket
import select


class Client:
    """Client to connect to the monodrive simulator"""

    def __init__(self, ip, port):
        """ Constructor.

        Args:
            ip(str):  The IP address of the simulator
            port(str): The port for the simulator
        """
        # The IP address of the simulator server
        self.__ip = ip
        # The port for the simulator server
        self.__port = port
        # The socket used to communicate with the server
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The status of the connection
        self.__connected = False

    @property
    def ip(self):
        """Get the IP of the server

        Returns:
            A string of the current server IP address.
        """
        return self.__ip

    @property
    def port(self):
        """Get the port of the server

        Returns:
            An integer with the current server port
        """
        return self.__port

    @property
    def connected(self):

        return self.__connected

    def connect(self):
        """ Establish a connection with the server.

        Returns:
            True if the server successfully connected, False otherwise.
        """
        try:
            self.__sock.connect((self.__ip, self.__port))
        except Exception as e:
            print("There was an error connecting to the socket at {}:{} - {}".format(
                self.__ip, self.__port, e))
            return False
        self.__connected = True
        return self.connected

    def disconnect(self):
        """Disconnect from the server."""
        self.__sock.close()
        self.__connected = False

    def read(self, length):
        """Read data from the server.

        Args:
            length(int): The length, in bytes, of data to read

        Returns:
            The binary data that was read from the server of size `length`
            or smaller.
        """
        data = b''
        count = 0
        while count < length:
            bytes = self.__sock.recv(length - count)
            if not bytes or len(bytes) == 0:
                break

            data = data + bytes
            count = count + len(bytes)

        return data

    def write(self, message):
        """Write data to the server.

        Args:
            message(bytearray): The binary message to write to the server

        """
        self.__sock.sendall(message)

    def data_ready(self):
        """Polls for available data on socket connection.

        Returns:
            True if there is available data to read from socket
        """
        if not self.__connected:
            return False
        ready = select.select([self.__sock], [], [], 0)
        return len(ready[0]) == 1
