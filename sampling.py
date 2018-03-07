import FreeCAD
import FreeCADGui
import Part
import Draft

__Title__="AM Sampling"
__Author__ = "Ingrid Fjordheim Onstein"
__Version__ = "0.1"
__Date__    = "2018-03-05"

__Comment__ = "This is the comment of the macro"
#__Icon__  = "/usr/lib/freecad/Mod/plugins/icons/Title_Of_macro"
#__IconW__  = "C:/Documents and Settings/YourUserName/Application Data/FreeCAD"
__Help__ = "start the macro and follow the instructions"
__Status__ = "unstable"
__Requires__ = "freecad 0.16"

#FreeCAD.Console.PrintMessage('Hello, World!')

#Get the selected object and prints the area
selected = FreeCADGui.Selection.getSelectionEx()
so = selected[0].SubObjects[0]
FreeCAD.Console.PrintMessage(so.Area)

#Get parameter range of sub object
pRange = so.ParameterRange
umin = int(pRange[0])
umax = int(pRange[1])
vmin = int(pRange[2])
vmax = int(pRange[3])

sampling = []
stepu = 10
stepv = 10
tolerance = 0

#sample in u-v direction along sub object with given step in u anv v direction
for su in range(umin, umax+stepu, stepu):
    for sv in range(vmin, vmax+stepv, stepv):
        vec = so.valueAt(su,sv)
        if so.isInside(vec,tolerance,True):
            sampling.append(vec)
            Draft.makePoint(vec.x, vec.y, vec.z)


        #sample = "(%s, %s)" % (su, sv)
        #sampling.append(sample)

#FreeCAD.Console.PrintMessage(sampling)
FreeCAD.Console.PrintMessage(sampling[1])
#Draft.makePoint(sampling[1].x, sampling[1].y, sampling[1].z)
#FreeCAD.Console.PrintMessage(pRange)
