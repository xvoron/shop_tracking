import cv2
import numpy as np
from server import ServerSocket
import argparse
from socket import gethostbyname


IP = gethostbyname('shop_visual_container')
PORT = 9999
HEADERSIZE = 20
PATH = '~/projects/shop_tracker/shop/'
DOCKER_PATH = '/usr/src/shopapp/data/'
VIDEO_NAME = 'shop_tracking_video.avi'


class TrackingObject:
    def __init__(self, box, centroid):
        self.ID = None
        self.color = None
        self.box = box
        self.centroid = centroid
        self.centroids = [self.centroid]

    def update(self, box, centroid):
        self.box = box
        self.centroid = centroid

        if len(self.centroids) > 10:
            self.centroids.pop(0)
        self.centroids.append(self.centroid)

class VisualApp:
    def __init__(self, path=None):
        self.socket = ServerSocket(IP, PORT, HEADERSIZE)
        self.received_data = []
        self.imgs_processed = []
        self.path = path if path != None else DOCKER_PATH
        self.video_name = VIDEO_NAME

    def start(self):
        while True:
            data = self.socket.receive_data()
            if data == -1:
                self.socket.close_socket()
                break
            else:
                self.received_data.append(data)

        self.process_all_data()
        self.write_video()
        self.socket.close_socket()

    def process_all_data(self):
        for data in self.received_data:
            img = self.process_image(data["img"], data["info"])
            self.imgs_processed.append(img)

    def process_image(self, img, out):
        out = out.values()
        for o in out:
            color = o.color
            box = o.box
            centroid = o.centroid
            pts = np.array(o.centroids)

            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                    color=color, thickness=4)

            cv2.circle(img, centroid, 5, color, -1)

            pad_x, pad_y = 1, 10
            org = (box[0]+pad_x, box[1]-pad_y)
            ID = o.ID
            cv2.putText(img, f"ID: {ID}", org, cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    color=color, thickness=3)

            cv2.polylines(img, [pts], False, color, thickness=2)
            for c in o.centroids:
                cv2.circle(img, c, 3, color, -1)

        return img

    def write_video(self):
        print(self.imgs_processed)
        img = self.imgs_processed[0]
        print(img)
        h, w, layers = img.shape
        framerate = 5

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(self.path + self.video_name, fourcc,  framerate, (w, h))

        for img in self.imgs_processed:
            video.write(img)

        cv2.destroyAllWindows()
        video.release()

if __name__ == "__main__":

    parser_help = "Running visualization application in docker using path \
                   to save video."
    parser = argparse.ArgumentParser(description=parser_help)
    path_help = "Path to save video output"
    parser.add_argument("-p", "--path", help=path_help)
    args = parser.parse_args()

    if args.path:
        path = args.path
    else:
        path = DOCKER_PATH

    visual = VisualApp(path)
    visual.start()

