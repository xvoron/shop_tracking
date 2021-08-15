"""Handler functions and class to manage data """
import cv2
import glob
import os
import xml.etree.ElementTree as ET
import time
import numpy as np


class DataFrame:
    """DataFrame class

    Encapsulate data about image and bounding boxes.
    """

    def __init__(self, xml, path:str):
        self.img_name, self.boxes = self._extract_info(xml)
        self.img = self._load_image(path)

    def _extract_info(self, xml):
        tree = ET.parse(xml)
        root = tree.getroot()

        information = dict()
        all_boxes = []
        all_centroids = []

        for obj in root.iter('object'):
            img_name = root.find('filename').text
            label = obj.find('name').text

            ymin, xmin, ymax, xmax = None, None, None, None
            centroid = None

            ymin = int(obj.find("bndbox/ymin").text)
            xmin = int(obj.find("bndbox/xmin").text)
            ymax = int(obj.find("bndbox/ymax").text)
            xmax = int(obj.find("bndbox/xmax").text)

            box = [xmin, ymin, xmax, ymax]
            all_boxes.append(box)

        return img_name, all_boxes

    def _load_image(self, path):
        img = cv2.imread(path+self.img_name)
        return img


def load_images_from_dir(path):
    """Load images from the path to list"""
    imgs = [{'img':cv2.imread(file), 'filename': str(file)} for file in glob.glob(path)]
    return imgs

def load_xml_from_dir(path: str):
    """Load sorted xml files to list"""
    xmls = sorted([file for file in glob.glob(path)])
    return xmls


if __name__ == "__main__":
    path_xml = 'shop/*.xml'
    xmls = load_xml_from_dir(path_xml)
