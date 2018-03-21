import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np

import Sampling
import Path


class SubObject(object):
    sampling = []
    path = []

    def __init__(self, subObject):
        self.subObject = subObject

    def sample(self, ustep, vstep, tolerance):
        pass


def getSubObject():
    try:
        selected = FreeCADGui.Selection.getSelectionEx()
        subObject = selected[0].SubObjects[0]

        FreeCADGui.Selection.clearSelection()

        return subObject
    except Exception as e:
        FreeCAD.Console.PrintError("\nNo object selected")

######################################################################
# Main
######################################################################
def main():
    FreeCAD.Console.PrintMessage("\n==== START ====\n")

    # Create subObject
    sub = SubObject(getSubObject())

    # Try to sample subObject
    if sub.subObject != None:
        #input: desired step in mm
        ustep = 10.0
        vstep = 10.0
        tolerance = 10.0
        sub.sampling = Sampling.sample(sub.subObject, ustep, vstep, tolerance)

        #sub.path = Path.generate_path(sub.subObject, sub.sampling)

    FreeCAD.Console.PrintMessage("\n==== DONE ====\n")

if __name__ == "__main__":
    main()

#Make B-spline
"""
points = sub.sampling[:31]
for vec in reversed(sub.sampling[32:64]):
  points.append(vec)
points += sub.sampling[64:96]
for vec in reversed(sub.sampling[96:128]):
  points.append(vec)
Draft.makeBSpline(points,closed=False,face=False,support=None)
"""
