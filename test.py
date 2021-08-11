from load_images import load_images_from_dir
from track import TrackingObject, Tracker
import unittest

class TestUnits(unittest.TestCase):

    def test_calc_centroid(self):
        tracker = Tracker()
        obj1 = dict()
        obj2 = dict()
        obj1["box"] = [0, 0, 100, 100]
        obj2["box"] = [1000, 1000, 1500, 1500]
        out1 = tracker._calc_centroid(obj1["box"])
        out2 = tracker._calc_centroid(obj2["box"])
        self.assertEqual(out1, [50,50])
        self.assertEqual(out2, [1250,1250])

    def test_tracker(self):
        tracker = Tracker()
        obj1 = dict()
        obj2 = dict()
        obj3 = dict()
        obj1["box"] = [0, 0, 100, 100]
        obj2["box"] = [1000, 1000, 1500, 1500]
        objs = [obj1, obj2]
        out1 = tracker.update(objs)
        obj1["box"] = [5, 5, 105, 105]
        obj2["box"] = [1003, 1003, 1503, 1503]
        obj3["box"] = [2000, 2000, 3500, 3500]
        objs = [obj1, obj2, obj3]
        out2 = tracker.update(objs)
        self.assertEquals([out1[0].ID, out1[1].ID], [0, 1])
        self.assertEquals([out2[0].ID, out2[1].ID, out2[2].ID], [0, 1, 2])




if __name__ == "__main__":
    unittest.main()
