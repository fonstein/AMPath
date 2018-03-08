import FreeCAD
import FreeCADGui
import Part
import Draft

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
        for su in range(umin, umax+ustep, ustep):
            for sv in range(vmin, vmax+vstep, vstep):
                vec = self.subObject.valueAt(su,sv)
                if self.subObject.isInside(vec,tolerance,True):
                    self.sampling.append(vec)
                else:
                    pass

    def displaySampling(self):
        if len(self.sampling) > 0:
            for vec in self.sampling:
                Draft.makePoint(vec.x, vec.y, vec.z)
        else:
            FreeCAD.Console.PrintError("There are no points to display")

def getSubObject():
    try:
        selected = FreeCADGui.Selection.getSelectionEx()
        subObject = selected[0].SubObjects[0]
        return subObject
    except Exception as e:
        FreeCAD.Console.PrintError("No object selected")


sub = SubObject(getSubObject())
if sub.subObject != None:
    sub.sampleSubObject(10, 10, 0.0)
    #sub.displaySampling()
else:
    pass
    #FreeCAD.Console.PrintError("No object selected")
