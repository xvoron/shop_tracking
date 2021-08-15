import socket
import pickle
import cv2
import time

class ServerSocket:
    """Open server socket to receive data form tracking component.

    Note:
        Using pickle library to decode received data as python objects.

    Attributes:
        ip (str): Server IP address.
        port (int): Port to connect.
        headersize (int): Size of header, contain information about data
                          length, if all data send, contain -1.
    """
    def __init__(self, ip, port, headersize):
        self.ip = ip
        self.port = port
        self.headersize = headersize
        self.buffersize = 4096
        self.queuesize = 10

    def open_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(self.queuesize)
        print("Server socket is open")
        self.connection, self.address = self.sock.accept()
        print("Server socket is connected")

    def close_socket(self):
        self.sock.close()
        time.sleep(0.5)

    def receive_data(self):
        try:
            data = self.recvall_header()
            print("Receive data")
            return data

        except Exception as e:
            print(e)
            self.close_socket()
            self.open_socket()

    def recvall_header(self):
        """Handler receive all data including message header using
        temporary buffer
        """
        buf = b''
        new_msg = True
        data = None

        while True:
            msg = self.connection.recv(self.buffersize)

            if new_msg and msg != b'':
                header = msg[:self.headersize]

                if int(header) == -1:   # end of data stream
                    print("End message")
                    return -1

                msg_len = int(header)
                print(f"Message length: {msg_len}")
                new_msg = False

            buf += msg

            if len(buf) - self.headersize == msg_len:
                data = pickle.loads(buf[self.headersize:])
                new_msg = True
                buf = b''
                break

        return data
