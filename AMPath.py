import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np
import random
import TSP_mod

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

        self.sample_subObject2()
        #self.sample_subObject_adaptiv()

    def calibrate_step(self):
        accuracy = 6
        u_calibrated = False
        v_calibrated = False
        while not (u_calibrated and v_calibrated):
            u_rand = random.uniform(self.subObject.ParameterRange[0], self.subObject.ParameterRange[1])
            v_rand = random.uniform(self.subObject.ParameterRange[2], self.subObject.ParameterRange[3])
            try:
                dist_v = self.calculate_dist((u_rand, v_rand), (u_rand, v_rand+self.vstep))
                dist_u = self.calculate_dist((u_rand, v_rand), (u_rand+self.ustep, v_rand))
            except Exception as e:
                FreeCAD.Console.PrintError("\nCould not calculate dist: %s" % (e))

            else:
                if (not v_calibrated) and (dist_v > (self.vdist + self.vdist/accuracy) or dist_v < (self.vdist - self.vdist/accuracy)):
                    prev = self.vstep
                    self.vstep = self.vstep*self.vdist/dist_v
                else:
                    v_calibrated = True

                if (not u_calibrated) and (dist_u > (self.udist + self.udist/accuracy) or dist_u < (self.udist - self.udist/accuracy)):
                    prev = self.ustep
                    self.ustep = self.ustep*self.udist/dist_u
                else:
                    u_calibrated = True

    def calibrate_step2(self, u_c, v_c, ustep, vstep, dist_d):
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
        pRange = self.subObject.ParameterRange
        umin = pRange[0]
        umax = pRange[1]
        vmin = pRange[2]
        vmax = pRange[3]

        self.calibrate_step()
        #[self.ustep, dummy] = self.calibrate_step2(umin, vmin, self.ustep, 0.0, self.udist)
        #[dummy, self.vstep] = self.calibrate_step2(umin, vmin, 0.0, self.vstep, self.vdist)

        """sample in u-v direction along sub object with given distance in u anv v direction"""
        for su in np.arange(umin, umax+self.ustep, self.ustep):
            for sv in np.arange(vmin, vmax+self.vstep, self.vstep):
                vec = self.subObject.valueAt(su,sv)
                if self.subObject.isInside(vec,self.tolerance,True):
                    #nvec = self.subObject.normalAt(su, sv)
                    samp = Sample(self.subObject, su, sv)
                    self.sampling.append(samp)
                else:
                    pass

    def sample_subObject2(self):
        pRange = self.subObject.ParameterRange
        umin = pRange[0]
        umax = pRange[1]
        vmin = pRange[2]
        vmax = pRange[3]

        u = umin
        v = vmin
        self.sampling.append(Sample(self.subObject, u, v))  #Add initial point

        while u < umax:
            while v < vmax:
                [dummy, self.vstep] = self.calibrate_step2(u, v, 0.0, self.vstep, self.vdist)
                v = v + self.vstep
                vec = self.subObject.valueAt(u, v)
                if self.subObject.isInside(vec, self.tolerance, True):
                    self.sampling.append(Sample(self.subObject, u, v))

            v = vmin
            [self.ustep, dummy] = self.calibrate_step2(u, v, self.ustep, 0.0, self.udist)
            u = u + self.ustep
            vec = self.subObject.valueAt(u, v)
            if self.subObject.isInside(vec, self.tolerance, True):
                self.sampling.append(Sample(self.subObject, u, v))

    def calculate_dist(self, (u1,v1), (u2,v2)):
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
            #FreeCADGui.Selection.clearSelection()
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

        #Draft.makeBSpline(path_vec, closed=False, face=False, support=None)
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

    def greedy_weighted(self, sample):
        coord = self.point_cloud        #Copy of point cloud (list of Sample objects)
        path = []                       #Empty list for the path

        current_sample = sample

        coord.remove(current_sample)    #Removes the starting point from the list
        path.append(current_sample)     #Appends the starting point to the path

        n = len(coord)

        for n in range(n):
            current_dist = float("inf")

            #Different types of weighting. Set the desired method to True and the rest to False
            y_weighted = False
            u_weighted = False
            normal_weighted = False
            xz_reward = True

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

                if normal_weighted:
                    norm1 = current_sample.nvec
                    norm2 = sample.nvec
                    norm_dist = math.sqrt(((norm2.x)-norm1.x)**2 + ((norm2.y)-norm1.y)**2 + (norm2.z-norm1.z)**2)
                    dist = math.sqrt(((vec2.x)-vec1.x)**2 + ((vec2.y)-vec1.y)**2 + (vec2.z-vec1.z)**2) + norm_dist*10

                if xz_reward:
                    dist = math.sqrt((((vec2.x)-vec1.x)/2.0)**2 + (vec2.y-vec1.y)**2 + ((vec2.z-vec1.z)/2.0)**2)

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

    def TSP(self):
        coord = []
        for point in self.point_cloud:
            coordinate = (point.x, point.y, point.z)
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
    p.get_subObjects(10.0, 10.0)
    p.generate_point_cloud()
    #p.display_sampling()

    #Test for Path
    path = Path(p.point_cloud)

    #GREEDY
    # path.greedy_algorithm(path.point_cloud[0])
    # path.display_path()

    #GREEDY WEIGHTED
    path.greedy_weighted(path.point_cloud[0])
    path.display_path()

    # #TSP
    # path.TSP()
    # path.display_path()

if __name__ == "__main__":
    main()
