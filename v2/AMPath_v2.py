import sys

# Has to be added to the path for FreeCAD to find the scripts
sys.path.append("C:/Users/ingridon/OneDrive/Documents/NTNU/Master/AMPath/v2")

import FreeCAD

import socket                       # Makes it possible to import script as module
import PointCloud as cloud
import PathGeneration as pathgen

import importlib as imp
imp.reload(cloud)                   # Reloades modules to catch potential edits
imp.reload(pathgen)                 # Reloades modules to catch potential edits

__title__ = "AMPath"
__author__ = "Ingrid Fjordheim Onstein"
__version__ = "0.2"
__doc__ = """Tool for generating paths for AM based on faces in STEP CAD models"""

def main():
    FreeCAD.Console.PrintMessage("\n\n============== START ==============")
    p = cloud.PointCloud()

    """Sampler overlate(r) med gitt avstand i mm """
    p.get_subObjects(10.0, 10.0)

    """Setter sammen alle samples i en punktsky"""
    p.generate_point_cloud()

    """Uncomment to display sampling"""
    # p.display_sampling()

    """Test for Path. Uncomment the deired path"""
    path = pathgen.Path(p.point_cloud)

    """GREEDY"""
    # path.greedy_algorithm(path.point_cloud[0])

    """GREEDY WEIGHTED. Uncomment desired weighting. U-weighting is default."""
    path.greedy_weighted(path.point_cloud[0], "u")
    # path.greedy_weighted(path.point_cloud[0], "y")

    """TSP"""
    # path.TSP_path()

    """Display path"""
    path.display_path()


if __name__ == "__main__":
    main()
