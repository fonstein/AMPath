import FreeCAD
import Draft
import math

import TSP_mod
import importlib as imp
imp.reload(TSP_mod)

class Path(object):
    def __init__(self, point_cloud):
        self.point_cloud = point_cloud
        self.path = []

    def display_path(self):
        path_vec = []
        for samp in self.path:
            path_vec.append(samp.vec)

        Draft.makeWire(path_vec, closed=False, face=False, support=None)

    def calculate_dist(self, vec1, vec2):
        dist = math.sqrt((vec2.x - vec1.x) ** 2 + (vec2.y - vec1.y) ** 2 + (vec2.z - vec1.z) ** 2)
        return dist

    def greedy_algorithm(self, sample):  # sample is the starting point
        coord = self.point_cloud  # Copy of point cloud (list of Sample objects)
        path = []  # Empty list for the path

        current_sample = sample

        coord.remove(current_sample)  # Removes the starting point from the list
        path.append(current_sample)  # Appends the starting point to the path

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
            current_sample = greedy_choice  # Sets the greedy choice to the current sample

        self.path = path  # Update path
        FreeCAD.Console.PrintMessage("\nGenerated greedy path.")

    def greedy_weighted(self, sample, weighting):  # weighting must be "u" or "y"
        coord = self.point_cloud  # Copy of point cloud (list of Sample objects)
        path = []  # Empty list for the path

        current_sample = sample
        greedy_choice = current_sample

        coord.remove(current_sample)  # Removes the starting point from the list
        path.append(current_sample)  # Appends the starting point to the path

        n = len(coord)

        for n in range(n):
            current_dist = float("inf")

            for sample in coord:
                weight = 100.0
                vec1 = current_sample.vec
                vec2 = sample.vec

                if weighting == "y":
                    dist = math.sqrt(
                        (vec2.x - vec1.x) ** 2 + ((vec2.y + weight) - vec1.y) ** 2 + (vec2.z - vec1.z) ** 2)

                else:
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
            current_sample = greedy_choice  # Sets the greedy choice to the current sample

        self.path = path  # Update path
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
