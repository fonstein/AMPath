import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np


class Sample(object):
    def __init__(self, subObject, u, v, vec, nvec):
        self.subObject = subObject
        self.u = u
        self.v = v
        self.vec = vec
        self.x = vec.x
        self.y = vec.y
        self.z = vec.z
        self.nvec = nvec

class SubObject(object):
    sampling = []

    def __init__(self, subObject):
        self.subObject = subObject

    def sampleSubObject(self, ustep, vstep, tolerance):
        pRange = self.subObject.ParameterRange
        umin = int(pRange[0])
        umax = int(pRange[1])
        vmin = int(pRange[2])
        vmax = int(pRange[3])

        """sample in u-v direction along sub object with given step in u anv v direction"""
        for su in np.arange(umin, umax+ustep, ustep):
            for sv in np.arange(vmin, vmax+vstep, vstep):
                vec = self.subObject.valueAt(su,sv)
                if self.subObject.isInside(vec,tolerance,True):
                    nvec = self.subObject.normalAt(su, sv)
                    samp = Sample(self, su, sv, vec, nvec)
                    self.sampling.append(samp)
                else:
                    pass

    def displaySampling(self):
        if len(self.sampling) > 0:
            for samp in self.sampling:
                Draft.makePoint(samp.x, samp.y, samp.z)
            FreeCAD.Console.PrintMessage("\nPoints generated")
        else:
            FreeCAD.Console.PrintError("\nThere are no points to display")

class Path(object):
    dist_matrix = {}
    path = []

    def __init__(self, subObject):
        self.subObject = subObject

    def calculate_dist(self, (u1,v1), (u2,v2)):
        vec1 = self.subObject.subObject.valueAt(u1,v1)
        vec2 = self.subObject.subObject.valueAt(u2,v2)

        dist = math.sqrt((vec2.x-vec1.x)**2 + (vec2.y-vec1.y)**2 + (vec2.z-vec1.z)**2)
        return dist

    def mk_matrix(self):
        """Compute a distance matrix for a set of points.

        Uses function 'dist' to calculate distance between
        any two points.  Parameters:
        -coord -- list of tuples with coordinates of all points, [(x1,y1),...,(xn,yn)]
        -dist -- distance function
        """
        coord = []
        for sample in self.subObject.sampling:
            coord.append((sample.u, sample.v))

        n = len(coord)
        D = {}      # dictionary to hold n times n matrix
        for i in range(n-1):
            for j in range(i+1,n):
                (x1,y1) = coord[i]
                (x2,y2) = coord[j]

                D[i,j] = self.calculate_dist((x1,y1), (x2,y2))

                D[j,i] = D[i,j]
        self.dist_matrix = D

    def generate_path(self):
        self.mk_matrix() #Generate distance matrix

        self.path.append(self.subObject.sampling[0]) #Add first point

        #Implement greedy algorithm here

        #FreeCAD.Console.PrintMessage("Path: %s" % (self.path))

def getSubObject():
    try:
        selected = FreeCADGui.Selection.getSelectionEx()
        subObject = selected[0].SubObjects[0]
        return subObject
    except Exception as e:
        FreeCAD.Console.PrintError("\nNo object selected")

FreeCAD.Console.PrintMessage("\n==== START ====\n")

sub = SubObject(getSubObject())
if sub.subObject != None:
    sub.sampleSubObject(0.1, 0.1, 0.0)
    #sub.displaySampling()
    try:
        path = Path(sub)
        #path.mk_matrix() #calculate distance matrix
        #FreeCAD.Console.PrintMessage("\nDistance matrix: \n%s\n" % (sub.dist_matrix))

        path.generate_path()
    except Exception as e:
        FreeCAD.Console.PrintError("\n%s" % (e))

else:
    pass
    #FreeCAD.Console.PrintError("No object selected")

FreeCAD.Console.PrintMessage("\n==== DONE ====\n")

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
