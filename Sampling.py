import FreeCAD
import FreeCADGui
import Part
import Draft
import math
import numpy as np
import random

def sample(subObject, ustep, vstep, tolerance):
    samples = Sampling(subObject, ustep, vstep, tolerance)
    return samples.sampling

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

class Sampling(object):
    sampling = []
    def __init__(self, subObject, udist, vdist, tolerance):
        self.subObject = subObject
        self.udist = udist
        self.vdist = vdist
        self.ustep = udist
        self.vstep = vdist
        self.tolerance = tolerance

        self.sampleSubObject()
        self.displaySampling()

    def calibrate_step(self):
        dummy_list = []
        u_calibrated = False
        v_calibrated = False
        while not (u_calibrated and v_calibrated):
            FreeCAD.Console.PrintMessage("\nCalibrating")
            u_rand = random.uniform(self.subObject.ParameterRange[0], self.subObject.ParameterRange[1])
            v_rand = random.uniform(self.subObject.ParameterRange[2], self.subObject.ParameterRange[3])
            FreeCAD.Console.PrintMessage("\nCalculated rand")
            try:
                dist_v = self.calculate_dist((u_rand, v_rand), (u_rand, v_rand+self.vstep))
                dist_u = self.calculate_dist((u_rand, v_rand), (u_rand+self.ustep, v_rand))
                FreeCAD.Console.PrintMessage("\nPoints: (%s, %s), (%s, %s) and (%s, %s)"% (u_rand, v_rand, u_rand, v_rand+self.vstep, u_rand+self.ustep, v_rand ))
                FreeCAD.Console.PrintMessage("\nCalculated dist. u: %s v: %s" % (dist_u, dist_v))
            except Exception as e:
                FreeCAD.Console.PrintError("\nCould not calculate dist: %s" % (e))

            else:
                if (not v_calibrated) and (dist_v > (self.vdist + self.vdist/4.0) or dist_v < (self.vdist - self.vdist/4.0)):
                    prev = self.vstep
                    #self.vstep = (self.vstep**2)/dist_v
                    self.vstep = self.vstep*self.vdist/dist_v
                    FreeCAD.Console.PrintMessage("\nChanged step v from %s to: %s" % (prev, self.vstep))
                else:
                    v_calibrated = True
                    FreeCAD.Console.PrintMessage("\nv is calibrated")

                if (not u_calibrated) and (dist_u > (self.udist + self.udist/4.0) or dist_u < (self.udist - self.udist/4.0)):
                    prev = self.ustep
                    #self.ustep = (self.ustep**2)/dist_u
                    self.ustep = self.ustep*self.udist/dist_u
                    FreeCAD.Console.PrintMessage("\nChanged step u from %s to: %s" % (prev, self.ustep))
                else:
                    u_calibrated = True
                    FreeCAD.Console.PrintMessage("\nu is calibrated")

    def sampleSubObject(self):
        pRange = self.subObject.ParameterRange
        umin = pRange[0]
        umax = pRange[1]
        vmin = pRange[2]
        vmax = pRange[3]

        self.calibrate_step()

        """sample in u-v direction along sub object with given step in u anv v direction"""
        #FreeCAD.Console.PrintMessage("Parameter range: %s" % (str(pRange)))
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

    def calculate_dist(self, (u1,v1), (u2,v2)):
        vec1 = self.subObject.valueAt(u1,v1)
        vec2 = self.subObject.valueAt(u2,v2)

        dist = math.sqrt((vec2.x-vec1.x)**2 + (vec2.y-vec1.y)**2 + (vec2.z-vec1.z)**2)
        return dist

    def displaySampling(self):
        if len(self.sampling) > 0:
            for samp in self.sampling:
                Draft.makePoint(samp.x, samp.y, samp.z)
            FreeCAD.Console.PrintMessage("\nPoints generated")
        else:
            FreeCAD.Console.PrintError("\nThere are no points to display")
