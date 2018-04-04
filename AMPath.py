import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np
import random

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

    def __init__(self, subObject, udist, vdist, tolerance):
        self.subObject = subObject
        self.udist = udist
        self.vdist = vdist
        self.ustep = udist
        self.vstep = vdist
        self.tolerance = tolerance

        """THIS IS BAD CODE AND SHOULD BE FIXED SOME OTHER WAY"""
        #self.sampling[:] = []

        self.sample_subObject()

    def calibrate_step(self):
        u_calibrated = False
        v_calibrated = False
        while not (u_calibrated and v_calibrated):
            #FreeCAD.Console.PrintMessage("\nCalibrating")
            u_rand = random.uniform(self.subObject.ParameterRange[0], self.subObject.ParameterRange[1])
            v_rand = random.uniform(self.subObject.ParameterRange[2], self.subObject.ParameterRange[3])
            #FreeCAD.Console.PrintMessage("\nCalculated rand")
            try:
                dist_v = self.calculate_dist((u_rand, v_rand), (u_rand, v_rand+self.vstep))
                dist_u = self.calculate_dist((u_rand, v_rand), (u_rand+self.ustep, v_rand))
                #FreeCAD.Console.PrintMessage("\nPoints: (%s, %s), (%s, %s) and (%s, %s)"% (u_rand, v_rand, u_rand, v_rand+self.vstep, u_rand+self.ustep, v_rand ))
                #FreeCAD.Console.PrintMessage("\nCalculated dist. u: %s v: %s" % (dist_u, dist_v))
            except Exception as e:
                FreeCAD.Console.PrintError("\nCould not calculate dist: %s" % (e))

            else:
                if (not v_calibrated) and (dist_v > (self.vdist + self.vdist/6.0) or dist_v < (self.vdist - self.vdist/6.0)):
                    prev = self.vstep
                    #self.vstep = (self.vstep**2)/dist_v
                    self.vstep = self.vstep*self.vdist/dist_v
                    #FreeCAD.Console.PrintMessage("\nChanged step v from %s to: %s" % (prev, self.vstep))
                else:
                    v_calibrated = True

                if (not u_calibrated) and (dist_u > (self.udist + self.udist/6.0) or dist_u < (self.udist - self.udist/6.0)):
                    prev = self.ustep
                    #self.ustep = (self.ustep**2)/dist_u
                    self.ustep = self.ustep*self.udist/dist_u
                    #FreeCAD.Console.PrintMessage("\nChanged step u from %s to: %s" % (prev, self.ustep))
                else:
                    u_calibrated = True

    def sample_subObject(self):
        pRange = self.subObject.ParameterRange
        umin = pRange[0]
        umax = pRange[1]
        vmin = pRange[2]
        vmax = pRange[3]

        self.calibrate_step()

        FreeCAD.Console.PrintMessage("\nNumber of samples before isInside: %s" % (len(self.sampling)))

        """sample in u-v direction along sub object with given distance in u anv v direction"""
        for su in np.arange(umin, umax+self.ustep, self.ustep):
            for sv in np.arange(vmin, vmax+self.vstep, self.vstep):
                vec = self.subObject.valueAt(su,sv)
                if self.subObject.isInside(vec,self.tolerance,True):
                    nvec = self.subObject.normalAt(su, sv)
                    samp = Sample(self, su, sv, vec, nvec)
                    self.sampling.append(samp)
                else:
                    pass
                    #FreeCAD.Console.PrintMessage("\nNot inside: (%s, %s)" % (su, sv))
        FreeCAD.Console.PrintMessage("\nNumber of samples after isInside: %s" % (len(self.sampling)))

    def calculate_dist(self, (u1,v1), (u2,v2)):
        vec1 = self.subObject.valueAt(u1,v1)
        vec2 = self.subObject.valueAt(u2,v2)

        dist = math.sqrt((vec2.x-vec1.x)**2 + (vec2.y-vec1.y)**2 + (vec2.z-vec1.z)**2)
        return dist

    def __str__(self):
        str = "\nLength of sampling: %s" % (len(self.sampling))
        return str

class PointCloud(object):
    point_cloud = []
    sub_objects = []
    num_so = 0

    def get_subObjects(self):
        ustep = 10.0
        vstep = 10.0
        tolerance = 10.0
        display = False

        try:
            selected = FreeCADGui.Selection.getSelectionEx()
            FreeCADGui.Selection.clearSelection()
        except Exception as e:
            FreeCAD.Console.PrintError("\nNo object selected")
        else:
            self.num_so = len(selected[0].SubObjects)
            FreeCAD.Console.PrintMessage("\nNumber of selected subObjects: %s" % (self.num_so))
            #Iterate over and sample selected sub objects
            for sub_object in selected[0].SubObjects:
                sub = None
                sub = SubObject(sub_object, ustep, vstep, tolerance)
                FreeCAD.Console.PrintMessage(sub)
                self.sub_objects.append(sub)
                FreeCAD.Console.PrintMessage(self)

            #self.display_sampling()

    def display_sampling(self):
        FreeCAD.Console.PrintMessage(self)
        if len(self.sub_objects) > 0:
            for sub in self.sub_objects:
                FreeCAD.Console.PrintMessage(sub)
                FreeCAD.Console.PrintMessage("\nNumber of samples to display: %s\n" % (len(sub.sampling)))
                for samp in sub.sampling:
                    Draft.makePoint(samp.x, samp.y, samp.z)
            FreeCAD.Console.PrintMessage("\nPoints generated")
        else:
            FreeCAD.Console.PrintError("\nThere are no points to display")

    def generate_point_cloud(self):
        pass

    def __str__(self):
        str = "\nNumber of sub objects: %s" % (len(self.sub_objects))
        return str


def main():
    FreeCAD.Console.PrintMessage("\n\n============== START ==============")
    p = PointCloud()
    p.get_subObjects()

    FreeCAD.Console.PrintMessage("\n\nFinal check before finish\n")
    FreeCAD.Console.PrintMessage(p)
    for so in p.sub_objects:
        FreeCAD.Console.PrintMessage(so)


if __name__ == "__main__":
    main()
