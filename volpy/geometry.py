import numpy as np
from sympy import symbols
from sympy import integrate
from scipy.spatial import Delaunay

from coordinates import CartesianCoordinate
from utils import print_progress

class Line2D():
    """A 2-Dimensional line"""
    def __init__(self,
                 point_A: CartesianCoordinate,
                 point_B: CartesianCoordinate):
        """Constructor

        Arguments:
        point_A: Cartesian Coordinate for point A
        point_B: Cartesian Coordinate for point B
        """
        self.point_A = point_A
        self.point_B = point_B

    def get_line_equation(self):
        """Returns a callable f(x): the line equation that connects point_A to
        point_B
        """
        if self.point_B.x - self.point_A.x == 0: # line parallel to the y axis
            return None
        else:
            slope = (self.point_B.y - self.point_A.y) /\
                    (self.point_B.x - self.point_A.x)
            linear_constant = -slope*self.point_A.x + self.point_A.y
            x = symbols('x')
            return slope*x + linear_constant

class Triangle():
    """A triangle in a 3D Cartesian Coordinates System"""
    def __init__(self,
                 point_A: CartesianCoordinate,
                 point_B: CartesianCoordinate,
                 point_C: CartesianCoordinate):
        self.point_A = point_A
        self.point_B = point_B
        self.point_C = point_C

    def get_plane_equation(self):
        """
        Returns the plane equation constants for the plane that contains points
        A, B and C.
        Plane equation: a*(x-xo) + b*(y-yo) + c*(z-zo) = 0
        """
        vector_AB = self.point_B - self.point_A
        vector_BC = self.point_C - self.point_B
        normal_vector = np.cross(vector_AB, vector_BC)
        a = normal_vector[0]
        b = normal_vector[1]
        c = normal_vector[2]
        xo = self.point_A.x
        yo = self.point_A.y
        zo = self.point_A.z
        x, y = symbols('x y') # z = f(x, y)
        return ((-a*(x-xo)-b*(y-yo))/c)+zo

    def get_volume(self):
        """
        Returns the volume from the polyhedron generated by triangle ABC and
        the XY plane
        """
        plane = self.get_plane_equation()
        # Define how to compute a double integral
        def compute_double_integral(outer_boundary_from,
                                    outer_boundary_to,
                                    line_from_equation,
                                    line_to_equation):
            if ((line_from_equation is None) or (line_to_equation is None)):
                return 0.0 # vertical line
            x, y = symbols('x y')
            volume =  integrate(plane,
                                (y, line_from_equation, line_to_equation),
                                (x, outer_boundary_from, outer_boundary_to))
            return volume

        # Instantiate lines. Points are sorted on the x coordinate.
        points = [self.point_A, self.point_B, self.point_C]
        points.sort()
        sorted_point_A, sorted_point_B, sorted_point_C = points
        lineAB = Line2D(sorted_point_A, sorted_point_B)
        lineBC = Line2D(sorted_point_B, sorted_point_C)
        lineAC = Line2D(sorted_point_A, sorted_point_C)

        # Compute double integral 1:
        volume1 = compute_double_integral(sorted_point_A.x,
                                          sorted_point_B.x,
                                          lineAC.get_line_equation(),
                                          lineAB.get_line_equation())
        # Compute double integral 2:
        volume2 = compute_double_integral(sorted_point_B.x,
                                          sorted_point_C.x,
                                          lineAC.get_line_equation(),
                                          lineBC.get_line_equation())

        # Sum and return
        total_volume = abs(volume1) + abs(volume2)
        return total_volume

class TriangularMesh(object):

    def __init__(self, point_cloud):
        """
        Arguments:
        point_cloud: a pandas dataframe containing x, y, z, elevation
        """
        self.point_cloud = point_cloud
        self.data = Delaunay(self.point_cloud[['x', 'y']]).simplices

    def get_volume(self):
        # consider implementing this with a level input.
        mesh_volume = 0
        iteration = 0
        data_amount = len(self.data)
        for i in range(data_amount):
            A = self.point_cloud.iloc[self.data[i][0]]
            B = self.point_cloud.iloc[self.data[i][1]]
            C = self.point_cloud.iloc[self.data[i][2]]
            point_A = CartesianCoordinate(A['x'], A['y'], A['z'])
            point_B = CartesianCoordinate(B['x'], B['y'], B['z'])
            point_C = CartesianCoordinate(C['x'], C['y'], C['z'])
            triangle = Triangle(point_A, point_B, point_C)
            volume = triangle.get_volume()
            mesh_volume += volume
            # update progress bar
            iteration += 1
            print_progress(iteration,
                           data_amount,
                           prefix='Progress:',
                           suffix='Complete',
                           length = 50)
        return mesh_volume