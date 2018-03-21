import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np
import SubObject

class PointCloud(object):
    point_cloud = []

    def get_subObject(self):
        subObject = SubObject.getSubObject()
        self.point_cloud.append(subObject)

    def generate_point_cloud(self):
        self.get_subObject()

    """
    Find some way to select multiple surface and sample one at a time as a subObject
    """
def main():
    p = PointCloud()
    p.generate_point_cloud()

if __name__ == "__main__":
    main()
