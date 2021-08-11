import socket
import pickle
import cv2
import numpy as np
import time


class Data:
    def __init__(self, ID, img):
        self.ID = ID
        self.img = img


class ClientSocket:
    def __init__(self, ip, port, headersize):
        self.ip = ip
        self.port = port
        self.headersize = headersize

    def close_connection(self):
        self.sock.close()

    def connect2server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
        except Exception as e:
            print(e)

    def send_data_header(self, data):
        try:
            data_send = pickle.dumps(data)
            data_send = bytes(f"{len(data_send):<{self.headersize}}", "utf-8") + data_send
            self.sock.sendall(data_send)
            time.sleep(2)
            print("Data send")
        except Exception as e:
            print(e)
            self.sock.close()
            self.connect2server()

    def send_finish(self):
            data_send = bytes(f"{-1:<{self.headersize}}", "utf-8")
            self.sock.sendall(data_send)
            time.sleep(0.5)
            self.sock.close()
            print("Finish sending")


if __name__ == "__main__":
    img = cv2.imread("shop/youtube_shop0086.jpg")
    data = Data(1, img)

    ip = 'localhost'
    port = 12002
    headersize = 20
    sock = ClientSocket(ip, port, headersize)
    sock.send_data_header(data)
    sock.send_finish()

