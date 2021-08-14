from visual import VisualApp, ServerSocket
import cv2
from collections import OrderedDict

class TestServerSocket:

    def test_open_close_socket(self):
        pass

class TestVisualApp:

    def test_process_image(self):
        img = cv2.imread("../shop/youtube_shop0086.jpg")
        info = OrderedDict()



