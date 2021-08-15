import socket
import pickle
import cv2
import numpy as np
import time


class ClientSocket:
    """ClientSocket manage connecting to server and send python objects
       using pickle library. 

    Attributes:
        ip (str): Server IP address.
        port (int): Port to connect.
        headersize (int): Size of header, contain information about data
                          length, if all data send, contain -1.
    """
    def __init__(self, ip:str, port:int, headersize:int):
        self.ip = ip
        self.port = port
        self.headersize = headersize

    def close_connection(self):
        self.sock.close()
        print("[Info] Socket was closed")

    def connect2server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            print(f"[Info] Connected to server {self.ip}:{self.port}")
        except Exception as e:
            print(e)

    def send_data_header(self, data):
        try:
            # pickle library to send python object
            data_send = pickle.dumps(data)
            # append header to sending data
            data_send = bytes(f"{len(data_send):<{self.headersize}}", "utf-8") + data_send
            self.sock.sendall(data_send)
            print(f"[Info] Data send: {len(data_send)}")
            time.sleep(1)
        except Exception as e:
            print(e)
            self.sock.close()
            self.connect2server()

    def send_finish(self):
            data_send = bytes(f"{-1:<{self.headersize}}", "utf-8")
            self.sock.sendall(data_send)
            time.sleep(0.5)
            self.sock.close()
            print("[Info] Finish sending, close socket")
