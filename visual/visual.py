"""Visualization Component

Description:
    Start server and wait for data in form of TrakingObject class (images,
    IDs, bounding boxes).  After all necessary data was received starting
    to process images by adding ID number, bounding box and last 10
    centroids with different colors corresponding to different people on a
    frame.

    The result video output defined in `VIDEO_NAME` constant value
    is saved back to input path with 5 fps.
"""

import cv2
import numpy as np
from server import ServerSocket
import argparse
from socket import gethostbyname


# Config constants
try:
    IP = gethostbyname('shop_visual_container') # Docker usage
except:
    IP = 'localhost'    # For testing purposes 'localhost'.

PORT = 9999
HEADERSIZE = 20
PATH = '~/projects/shop_tracker/shop/'
DOCKER_PATH = '/usr/src/shopapp/data/'
VIDEO_NAME = 'shop_tracking_video.avi'


# TrackingObject class defined here to provide information to pickle about
# datatype of received data
class TrackingObject:
    """Contain all necessary information about tracking object"""

    def __init__(self, box, centroid):
        self.ID = None
        self.color = None
        self.box = box
        self.centroid = centroid
        self.centroids = [self.centroid]    # Historical centroids data

    def update(self, box, centroid):
        """Tracker updates data by this method"""
        self.box = box
        self.centroid = centroid

        if len(self.centroids) > 10:
            self.centroids.pop(0)
        self.centroids.append(self.centroid)


class VisualApp:
    """Manage opening socket to receive data, process, write result to file.

    Attributes:
        path (str): Path to files given implicitly by DOCKER_PATH or
                    explicitly using path as class attribute. The same path
                    is used to write output video file.
    """

    def __init__(self, path=None):
        self.socket = ServerSocket(IP, PORT, HEADERSIZE)
        self.received_data = []
        self.imgs_processed = []
        self.path = path if path != None else DOCKER_PATH
        self.video_name = VIDEO_NAME

    def start(self):
        self.socket.open_socket()
        while True:
            data = self.socket.receive_data()

            # "-1" payload notify the end of the data stream
            if data == -1:
                self.socket.close_socket()
                break
            else:
                self.received_data.append(data)

        self.process_all_data()
        self.write_video(self.imgs_processed)
        self.socket.close_socket()

    def process_all_data(self):
        """After receive all data process each frame"""
        for data in self.received_data:
            img = self.process_image(data["img"], data["info"])
            self.imgs_processed.append(img)

    def process_image(self, img, frame_information):
        """Add data to image.

        Args:
            img (np.array): Raw image.
            frame_information (OrderedDict): Each member is TrackingObject type;
                                             and hold information about one
                                             tracking person (object) on a
                                             frame.

        Returns:
            np.array: Processed image with ID, bounding box, centroid,
                      historical polyline
        """

        frame_information = frame_information.values()
        for obj in frame_information:

            color = obj.color
            box = obj.box
            centroid = obj.centroid
            pts = np.array(obj.centroids)

            # Add a bounding box to the image
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                    color=color, thickness=4)

            # Add centroid to the image
            cv2.circle(img, centroid, 5, color, -1)

            # Add ID on upper left corner above bounding box
            pad_x, pad_y = 1, 10
            org = (box[0]+pad_x, box[1]-pad_y)
            ID = obj.ID
            cv2.putText(img, f"ID: {ID}", org, cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    color=color, thickness=3)

            # Add historical polyline with centroids that represents person
            # movement history in the shop for the last 10 frames

            cv2.polylines(img, [pts], False, color, thickness=2)
            for c in obj.centroids:
                cv2.circle(img, c, 3, color, -1)

        return img

    def write_video(self, imgs):
        """Write processed images as video file with 5 fps frame rate"""

        img = imgs[0]
        h, w, layers = img.shape
        framerate = 5

        # Codec parameters
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(self.path + self.video_name, fourcc,  framerate, (w, h))

        for img in imgs:
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

