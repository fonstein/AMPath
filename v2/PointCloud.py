import FreeCAD
import FreeCADGui
import Draft

import socket
import SubObject as subobj

import importlib as imp
imp.reload(subobj)

class PointCloud(object):
    def __init__(self):
        self.sub_objects = []
        self.point_cloud = []
        self.num_so = 0

    def get_subObjects(self, ustep, vstep):
        tolerance = 10.0

        try:
            selected = FreeCADGui.Selection.getSelectionEx()
        except Exception as e:
            FreeCAD.Console.PrintError("\nNo object selected")
        else:
            self.num_so = len(selected[0].SubObjects)

            FreeCAD.Console.PrintMessage("\nNumber of sub objects: %s \n" % self.num_so)

            #Iterate over and sample selected sub objects
            for sub_object in selected[0].SubObjects:
                sub = subobj.SubObject(sub_object, ustep, vstep, tolerance)
                FreeCAD.Console.PrintMessage(sub)
                self.sub_objects.append(sub)


    def display_sampling(self):
        if len(self.point_cloud) > 0:
            FreeCAD.Console.PrintMessage("\nNumber of samples to display: %s\n" % (len(self.point_cloud)))
            for point in self.point_cloud:
                Draft.makePoint(point.vec.x, point.vec.y, point.vec.z)
        else:
            FreeCAD.Console.PrintError("\nThere are no points to display")

    def generate_point_cloud(self):
        for sub in self.sub_objects:
            for samp in sub.sampling:
                self.point_cloud.append(samp)   #Appends Sample object

    def __str__(self):
        str = "\nPointCloud: Number of sub objects: %s" % (len(self.sub_objects))
        return str
