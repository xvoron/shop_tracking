from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
from random import randint
from client import ClientSocket
from dataloader import DataFrame, load_xml_from_dir
import config


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


class Tracker:
    def __init__(self):
        self.max_num_id = 10
        self.next_id = 0
        self.objects = OrderedDict()

        self.disappeared = OrderedDict()
        self.max_disapper = 10

        self.max_objects = 10
        self.tracking_objects = [None] * self.max_objects
        self.Object = TrackingObject

    def register(self, obj):
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
    def __init__(self):
        self.socket = ClientSocket(config.ip, config.port,
                config.headersize)
        self.tracker = Tracker()
        self.data = None

    def load_data(self, path):
        xmls = load_xml_from_dir(path)
        self.data = [DataFrame(xml) for xml in xmls]

    def start_tracking(self):
        self.connect()
        self.load_data()

        for data in self.data:
            information = self.tracker.update(data.boxes)
            data2send = {"info": information, "img": data.img}
            self.send_data(data2send)
        self.send_data("end")

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
    tracker = TrackingApp()

