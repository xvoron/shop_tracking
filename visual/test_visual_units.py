from visual import VisualApp, ServerSocket, TrackingObject
import cv2
from collections import OrderedDict
import pytest
import os

PATH = '/../shop/'

def test_ServerSocket():
    socket = ServerSocket('localhost', 9999, 20)

def test_process_image():
    path2data = os.getcwd() + PATH + 'youtube_shop0086.jpg'
    img = cv2.imread(path2data)
    assert img is not None
    info = OrderedDict()
    obj = TrackingObject([0, 0, 100, 100], [50, 50])
    obj.ID = 0
    obj.color = (0, 0, 255)
    info[0] = obj
    visual_app = VisualApp()
    img = visual_app.process_image(img, info)
    assert img is not None

def test_write_video():
    path2data = os.getcwd() + PATH + 'youtube_shop0086.jpg'
    img = cv2.imread(path2data)
    path2save = os.getcwd() + PATH
    visual_app = VisualApp(path2save)
    imgs = [img, img]
    visual_app.write_video(imgs)
