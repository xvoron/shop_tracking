"""Tracking component

Description:
    TrackingApp managing loading xml data and image, apply tracking
    algorithm [1] to a frame. After frame was processed send image and data
    about tracking object (TrackingObject class) to Visualization Component
    in different docker container. After all data send close the socket and
    finish process.


[1] Tracking algorithm (Tracker class):
    Simply algorithm based on euclidean distance between centroids
    calculated from bounding boxes. If there is a new object tracker
    register that object with a new ID number. If some of the objects does
    not appear anymore tracker deregister particular object.

"""
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
from random import randint
from client import ClientSocket
from dataloader import DataFrame, load_xml_from_dir
import argparse
import time
import socket

# Config constants
try:
    IP = socket.gethostbyname('shop_visual_container')  # Docker usage
except:
    IP = 'localhost'    # For testing purposes 'localhost'.

PORT = 9999
HEADERSIZE = 20
PATH = '~/projects/shop_tracker/shop/'
DOCKER_PATH = '/usr/src/shopapp/data/'


class TrackingObject:
    """Contain all necessary information about tracking object"""

    def __init__(self, box, centroid):
        self.ID = None
        self.color = None
        self.box = box
        self.centroid = centroid
        self.centroids = [self.centroid]

    def update(self, box, centroid):
        """Tracker updates data by this method"""
        self.box = box
        self.centroid = centroid

        if len(self.centroids) > 10:
            self.centroids.pop(0)
        self.centroids.append(self.centroid)


class Tracker:
    """Simply algorithm based on euclidean distance between centroids
    calculated from bounding boxes.
    """
    def __init__(self):
        # maximum number of objects at one frame
        self.max_num_id = 100
        self.next_id = 0
        # storage for all TrackingObject's
        self.objects = OrderedDict()

        # objects that will disappear if they not captured again
        self.disappeared = OrderedDict()
        # maximum frames for disappear
        self.max_disapper = 10

        # number of stored objects (memory)
        self.max_objects = 100
        self.tracking_objects = [None] * self.max_objects
        self.Object = TrackingObject

    def register(self, obj):
        """Register object with given ID, add a random color

        Args:

        Returns:

        """
        self.objects[self.next_id] = obj
        self.objects[self.next_id].ID = self.next_id
        self.objects[self.next_id].color = (randint(0, 255), randint(0,
            255), randint(0, 255))
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def deregister(self, obj_id):
        del self.objects[obj_id]
        del self.disappeared[obj_id]

    def update(self, data):
        # If there is nothing to update, deregister objects that do not
        # appear in self.max_dissapper number of frames
        if len(data) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1

                if self.disappeared[obj_id] > self.max_disapper:
                    self.deregister(obj_id)

            return self.objects

        # reserve memory for input centroids
        input_centroids = np.zeros((len(data), 2), dtype="int")

        for (i, box) in enumerate(data):
            centroid = self._calc_centroid(box)
            input_centroids[i] = centroid
            self.tracking_objects[i] = self.Object(box, centroid)

        # if there is no tracking objects, register them
        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(self.tracking_objects[i])

        else:
            objects_ids = list(self.objects.keys())
            objects_centroids = list()

            for obj in list(self.objects.values()):
                objects_centroids.append(obj.centroid)

            D = dist.cdist(np.array(objects_centroids), input_centroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                obj_id = objects_ids[row]
                self.objects[obj_id].update(data[col],
                                            input_centroids[col])
                self.disappeared[obj_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            if D.shape[0] >= D.shape[1]:

                for row in unused_rows:
                    obj_id = objects_ids[row]
                    self.disappeared[obj_id] += 1

                    if self.disappeared[obj_id] > self.max_disapper:
                        self.deregister(obj_id)

            else:
                for col in unused_cols:
                    self.register(self.tracking_objects[col])

        return self.objects

    def _calc_centroid(self, box):
        xmin, ymin, xmax, ymax = box
        cx, cy = int((xmax-xmin)/2+xmin), int((ymax-ymin)/2+ymin)
        return [cx, cy]


class TrackingApp:
    def __init__(self, path=None):
        self.socket = ClientSocket(IP, PORT, HEADERSIZE)
        self.tracker = Tracker()
        self.data = None
        self.path = path if path != None else PATH


    def load_data(self):
        xmls = load_xml_from_dir(self.path + "*.xml")
        self.data = [DataFrame(xml, self.path) for xml in xmls]

    def start(self):
        time.sleep(2)
        self.connect()
        self.load_data()

        for data in self.data:
            information = self.tracker.update(data.boxes)
            data2send = {"info": information, "img": data.img}
            self.send_data(data2send)
        self.send_data("end")
        self.exit()

    def connect(self):
        self.socket.connect2server()

    def send_data(self, data):
        if data != "end":
            self.socket.send_data_header(data)
        else:
            self.socket.send_finish()

    def exit(self):
        self.socket.close_connection()


if __name__ == "__main__":

    parser_help = "Running tracking application in docker using path \
                   to files argument."
    parser = argparse.ArgumentParser(description=parser_help)
    path_help = "Path to files with *.xml and *.jpg extension"
    parser.add_argument("-p", "--path", help=path_help)
    args = parser.parse_args()

    if args.path:
        path = args.path
    else:
        path = DOCKER_PATH

    tracker = TrackingApp(path)
    tracker.start()

