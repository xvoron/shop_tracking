import cv2
import socket
import numpy as np

def process_image(img, out):
    out = out.values()
    for o in out:
        color = o.color
        box = o.box
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                color=color, thickness=4)
        centroid = o.centroid
        cv2.circle(img, centroid, 5, color, -1)
        pad_x, pad_y = 1, 10
        org = (box[0]+pad_x, box[1]-pad_y)
        ID = o.ID
        cv2.putText(img, f"ID: {ID}", org, cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                color=color, thickness=3)
        pts = np.array(o.centroids)
        cv2.polylines(img, [pts], False, color, thickness=2)
        for c in o.centroids:
            cv2.circle(img, c, 3, color, -1)

    return img

class VisualApp:
    def __init__(self):
        pass
