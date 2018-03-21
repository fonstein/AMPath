import FreeCAD
import FreeCADGui
import Part
import math
import numpy as np

"""This file has to be rewritten after reorganization in the other files.
   This file should only receive a point cloud and no subObject"""

def generate_path(point_cloud):
    p = Path(point_cloud)
    return p.path

class Path(object):
    dist_matrix = {}
    path = []

    def __init__(self, point_cloud):
        self.point_cloud = point_cloud

        self.mk_matrix()
        self.path.append(self.subObject.sampling[0])

    def calculate_dist(self, (u1,v1), (u2,v2)):
        vec1 = self.subObject.valueAt(u1,v1)
        vec2 = self.subObject.valueAt(u2,v2)

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
