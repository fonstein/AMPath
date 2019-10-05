import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np
import random
#import TSP_mod

__title__ = "AMPath"
__author__ = "Ingrid Fjordheim Onstein"
__version__ = "0.1"
__doc__ = """Tool for generating paths for AM based on faces in STEP CAD models"""

class Sample(object):
    def __init__(self, subObject, u, v):
        self.subObject = subObject
        self.u = u
        self.v = v

        self.vec = self.subObject.valueAt(u, v)
        self.nvec = self.subObject.normalAt(u, v)

class SubObject(object):
    def __init__(self, subObject, udist, vdist, tolerance):
        self.subObject = subObject
        self.udist = udist
        self.vdist = vdist
        self.ustep = udist
        self.vstep = vdist
        self.tolerance = tolerance

        self.sampling = []

        self.sample_subObject()

    def calibrate_step(self, u_c, v_c, ustep, vstep, dist_d):
        accuracy = 10
        calibrated = False
        while not calibrated:
            try:
                dist = self.calculate_dist((u_c, v_c), (u_c + ustep, v_c + vstep))
            except Exception as e:
                FreeCAD.Console.PrintError("\nCould not calculate dist: %s" % (e))
            else:
                if (not calibrated) and (dist > (dist_d + dist_d/accuracy) or dist < (dist_d - dist_d/accuracy)):
                    vstep = vstep*dist_d/dist
                    ustep = ustep*dist_d/dist
                else:
                    calibrated = True
        return ustep, vstep

    def sample_subObject(self):
        FreeCAD.Console.PrintMessage("\nSampling initiated\n")

        pRange = self.subObject.ParameterRange
        umin = pRange[0]
        umax = pRange[1]
        vmin = pRange[2]
        vmax = pRange[3]

        u = umin
        v = vmin
        self.sampling.append(Sample(self.subObject, u, v))  #Add initial point

        # Uncomment for non-adaptiv sampling
        #[dummy, self.vstep] = self.calibrate_step(u, v, 0.0, self.vstep, self.vdist)
        #[self.ustep, dummy] = self.calibrate_step(u, v, self.ustep, 0.0, self.udist)

        while u < umax:
            while v < vmax:
                [dummy, self.vstep] = self.calibrate_step(u, v, 0.0, self.vstep, self.vdist) # Comment for non-adaptiv sampling
                v = v + self.vstep
                vec = self.subObject.valueAt(u, v)
                if self.subObject.isInside(vec, self.tolerance, True):
                    self.sampling.append(Sample(self.subObject, u, v))

            v = vmin
            [self.ustep, dummy] = self.calibrate_step(u, v, self.ustep, 0.0, self.udist) # Comment for non-adaptiv sampling
            u = u + self.ustep
            vec = self.subObject.valueAt(u, v)
            if self.subObject.isInside(vec, self.tolerance, True):
                FreeCAD.Console.PrintMessage("\nAdding sample to sub object\n")
                self.sampling.append(Sample(self.subObject, u, v))

    def calculate_dist(self, u1, v1, u2, v2):
        vec1 = self.subObject.valueAt(u1,v1)
        vec2 = self.subObject.valueAt(u2,v2)

        dist = math.sqrt((vec2.x-vec1.x)**2 + (vec2.y-vec1.y)**2 + (vec2.z-vec1.z)**2)
        return dist

    def __str__(self):
        str = "\nLength of sampling: %s" % (len(self.sampling))
        return str

class PointCloud(object):
    def __init__(self):
        self.sub_objects = []
        self.point_cloud = []
        self.num_so = 0

    def get_subObjects(self, ustep, vstep):
        tolerance = 10.0
        display = False

        try:
            selected = FreeCADGui.Selection.getSelectionEx()
        except Exception as e:
            FreeCAD.Console.PrintError("\nNo object selected")
        else:
            self.num_so = len(selected[0].SubObjects)

            #Iterate over and sample selected sub objects
            for sub_object in selected[0].SubObjects:
                sub = SubObject(sub_object, ustep, vstep, tolerance)
                FreeCAD.Console.PrintMessage(sub)
                self.sub_objects.append(sub)
            FreeCAD.Console.PrintMessage(self)

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

class Path(object):
    def __init__(self, point_cloud):
        self.point_cloud = point_cloud
        self.path = []

    def display_path(self):
        path_vec = []
        for samp in self.path:
            path_vec.append(samp.vec)

        Draft.makeWire(path_vec,closed=False,face=False,support=None)

    def calculate_dist(self, vec1, vec2):
        dist = math.sqrt((vec2.x-vec1.x)**2 + (vec2.y-vec1.y)**2 + (vec2.z-vec1.z)**2)
        return dist

    def greedy_algorithm(self, sample): #sample is the starting point
        coord = self.point_cloud        #Copy of point cloud (list of Sample objects)
        path = []                       #Empty list for the path

        current_sample = sample

        coord.remove(current_sample)    #Removes the starting point from the list
        path.append(current_sample)     #Appends the starting point to the path

        n = len(coord)

        for n in range(n):
            greedy_choice = coord[0]
            current_dist = self.calculate_dist(current_sample.vec, greedy_choice.vec)
            for sample in coord[1:]:
                dist = self.calculate_dist(current_sample.vec, sample.vec)
                if dist < current_dist:
                    greedy_choice = sample
                    current_dist = dist
                else:
                    pass

            path.append(greedy_choice)
            coord.remove(greedy_choice)
            current_sample = greedy_choice  #Sets the greedy choice to the current sample

        self.path = path                #Update path
        FreeCAD.Console.PrintMessage("\nGenerated greedy path.")

    def greedy_weighted(self, sample, weighting): #weighting must be "u" or "y"
        coord = self.point_cloud        #Copy of point cloud (list of Sample objects)
        path = []                       #Empty list for the path

        current_sample = sample

        coord.remove(current_sample)    #Removes the starting point from the list
        path.append(current_sample)     #Appends the starting point to the path

        n = len(coord)

        for n in range(n):
            current_dist = float("inf")

            #Different types of weighting
            if weighting == "u":
                u_weighted = True
                y_weighted = False
            elif weighting == "y":
                u_weighted = False
                y_weighted = True
            else: #u-weighting is default
                u_weighted = True
                y_weighted = False


            for sample in coord:
                weight = 10.0
                vec1 = current_sample.vec
                vec2 = sample.vec

                if y_weighted:
                    dist = math.sqrt(((vec2.x)-vec1.x)**2 + ((vec2.y+weight)-vec1.y)**2 + (vec2.z-vec1.z)**2)

                if u_weighted:
                    if sample.u != current_sample.u:
                        dist = self.calculate_dist(current_sample.vec, sample.vec) + weight
                    else:
                        dist = self.calculate_dist(current_sample.vec, sample.vec)


                if dist < current_dist:
                    greedy_choice = sample
                    current_dist = dist
                else:
                    pass

            path.append(greedy_choice)
            coord.remove(greedy_choice)
            current_sample = greedy_choice  #Sets the greedy choice to the current sample

        self.path = path    #Update path
        FreeCAD.Console.PrintMessage("\nGenerated weighted greedy path.")

    def TSP_path(self):
        coord = []
        for point in self.point_cloud:
            coordinate = (point.vec.x, point.vec.y, point.vec.z)
            coord.append(coordinate)

        tsp_path = TSP_mod.run_TSP(coord)
        path = []
        for point in tsp_path:
            sample = self.point_cloud[point]
            path.append(sample)

        self.path = path
        FreeCAD.Console.PrintMessage("\nGenerated TSP path.")

def main():
    FreeCAD.Console.PrintMessage("\n\n============== START ==============")
    p = PointCloud()
    p.get_subObjects(1000.0, 1000.0)
    p.generate_point_cloud()

    """Uncomment to display sampling"""
    # p.display_sampling()

    """Test for Path. Uncomment the deired path"""
    # path = Path(p.point_cloud)

    """GREEDY"""
    # path.greedy_algorithm(path.point_cloud[0])

    """GREEDY WEIGHTED. Uncomment desired weighting. U-weighting is default."""
    # path.greedy_weighted(path.point_cloud[0], "u")
    # path.greedy_weighted(path.point_cloud[0], "y")

    """TSP"""
    # path.TSP_path()

    """Display path"""
    # path.display_path()

if __name__ == "__main__":
    main()
