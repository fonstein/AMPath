import FreeCAD
import math

from Sample import Sample

# import importlib as imp
# imp.reload(Sample)

class SubObject(object):
    def __init__(self, subObject, udist, vdist, tolerance):
        self.subObject = subObject
        self.udist = udist
        self.vdist = vdist
        self.ustep = udist
        self.vstep = vdist
        self.tolerance = tolerance

        self.sampling = []

        # self.sample_subObject()

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
