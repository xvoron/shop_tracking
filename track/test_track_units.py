from track import Tracker, TrackingApp, TrackingObject, ClientSocket, DataFrame, load_xml_from_dir
import os
import pytest
from collections import OrderedDict

PATH = '/../shop/'

def test_load_xml_from_dir():
    path2data = os.getcwd() + PATH + '*.xml'
    xmls = load_xml_from_dir(path2data)
    assert len(xmls) == 30

def test_DataFrame():
    path2data = os.getcwd() + PATH
    tracking_app = TrackingApp(path2data)
    tracking_app.load_data()
    assert len(tracking_app.data) == 30
    assert tracking_app.data[0].img_name == 'youtube_shop0086.jpg'

def test_tracker_register_deregister():
    box = [0, 0, 100, 100]
    tracker = Tracker()
    centroid = tracker._calc_centroid(box)
    assert centroid == [50, 50]

    with pytest.raises(TypeError):
        tracking_object = TrackingObject()

    tracking_object = TrackingObject(box, centroid)
    tracker.register(tracking_object)

    assert tracker.next_id == 1
    assert len(tracker.objects) == 1
    assert tracker.objects[0].ID == 0

    tracker.deregister(0)
    assert tracker.next_id == 1
    assert len(tracker.objects) == 0


def test_tracker_update():
    path2data = os.getcwd() + PATH
    tracking_app = TrackingApp(path2data)
    tracking_app.load_data()
    tracker = Tracker()

    boxes = tracking_app.data[0].boxes
    tracking_output = tracker.update(boxes)
    assert type(tracking_output) == OrderedDict

    assert len(tracking_output) == 3
    tracking_output = tracking_output.values()
    for obj in tracking_output:
        assert obj.ID in [0, 1, 2]

def test_client_socket():
    socket = ClientSocket('localhost', 9999, 20)
    socket.connect2server()
    socket.close_connection()
