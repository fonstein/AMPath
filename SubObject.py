import FreeCAD
import FreeCADGui
import Part
import math
import numpy as np
import Sampling

def getSubObject():
    try:
        selected = FreeCADGui.Selection.getSelectionEx()
        subObject = selected[0].SubObjects[0]

        FreeCADGui.Selection.clearSelection()

    except Exception as e:
        FreeCAD.Console.PrintError("\nNo object selected")
    else:
        sub = SubObject(subObject)
        if sub.subObject != None:
            #input: desired step in mm
            ustep = 10.0
            vstep = 10.0
            tolerance = 10.0
            sub.sampling = Sampling.sample(sub.subObject, ustep, vstep, tolerance, True)
            return sub

class SubObject(object):
    sampling = []

    def __init__(self, subObject):
        self.subObject = subObject
