# Two coordinate systems are used in this program:
# 1) Default CS (x0, y0) - pixel indexing. Starts from the upper left corner of the camera's matrix.
# 2) Central CS (x, y) - Starts from the centre of the camera's matrix. The X-axis points right and
#   the Y-axis points up.
#
# Final coordinates are returned in the default CS.
#
# Since there is no instruction in the problem formulation how to handle input values, I have implemented
# two possible ways:
# 1) Enter coordinates manually with spaces between them. Example:
#       python3 photogrammetry.py
#       >>> Enter coordinates with spaces (xl yl xr yr): 1045 0 648 0
#
# 2) Pass a file as an argument to the script. File must contain 4 coordinates in single line, separated
#    with spaces. Example:
#       python3 photogrammetry.py file.txt
#
#    Every line of output then will be corresponding to the line in provided file.
#    The output could be also saved as a file using:
#       python3 photogrammetry.py file.txt > output.txt
#
# P.S. I have also implemented distance error calculation, but this is not included into final result
# since there is no such instruction in the problem formulation. You can get the error using the
# DoubleCameraModel.obj_dist_err method.

import numpy as np
import sys


class CameraModel:
    def __init__(self, frame_width: float, frame_height: float, angle_of_view: float):
        self.width = frame_width
        self.height = frame_height
        self.aov = angle_of_view

        self.T_c = np.array([
            [1, 0, 0],
            [0, -1, 0],
            [-self.width / 2, self.height / 2, 1],
        ])

        self.T_d = np.linalg.inv(self.T_c)

    def to_central(self, x0: int, y0: int) -> np.array:
        """
        Coordinate transformation from default to central coordinates.
        """
        if x0 < 0 or y0 < 0:
            raise ValueError("Coordinate values must be greater than zero in default CS.")
        if x0 > self.width or y0 > self.height:
            raise ValueError("Coordinate values must not exceed frame width and height.")
        return (np.array([x0, y0, 1]) @ self.T_c)[:2]

    def to_default(self, x: int, y: int) -> np.array:
        """
        Coordinate transformation from central to default coordinates.
        """
        return (np.array([x, y, 1]) @ self.T_d)[:2]

    def obj_angle(self, x0: int, y0: int) -> float:
        """
        Returns TANGENT of the angle between the object and the central line of sight.
        > 0 if object is to the camera's right;
        < 0 if object is to the camera's left.
        """
        x, y = self.to_central(x0, y0)
        return np.tan(self.aov / 2) * x * 2 / self.width

    def obj_angle_err(self) -> float:
        return np.tan(self.aov / 2) * 2 / self.width


class DoubleCameraModel:
    def __init__(self, left: CameraModel, right: CameraModel, center: CameraModel, distance: float):
        """
        :param left: Left camera.
        :param right: Right camera.
        :param center: Hypothetical camera in the middle of the system.
        :param distance: Distance between two cameras.
        """
        self.left = left
        self.right = right
        self.center = center
        self.d = distance

    def obj_dist(self, left_coords: [int, int], right_coords: [int, int]) -> float:
        """
        Estimates distance to the object based on pixel coordinates from 2 cameras.
        """
        tl = self.left.obj_angle(*left_coords)
        tr = self.right.obj_angle(*right_coords)

        if (tl - tr) <= 0:
            raise ValueError('Incorrect coordinate values. Lines of sight of cameras do not cross.')

        return self.d / (tl - tr)

    def obj_dist_err(self, left_coords: [int, int], right_coords: [int, int]) -> float:
        """
        Calculates error of distance estimate.
        """
        tl = self.left.obj_angle(*left_coords)
        tr = self.right.obj_angle(*right_coords)
        tl_err = self.left.obj_angle_err()
        tr_err = self.right.obj_angle_err()
        dd_dtan = self.d / (tl - tr)**2

        return np.sqrt((dd_dtan * tl_err)**2 + (dd_dtan * tr_err)**2)

    def obj_coords(self, left_coords: [int, int], right_coords: [int, int]) -> [int, int, float]:
        """
        Calculates position of the object in the middle camera in default CS.
        The third coordinate is the z coordinate with the same unit as self.d
        """
        obj_dist = self.obj_dist(left_coords, right_coords)
        obj_angle = self.left.obj_angle(*left_coords) - (self.d / 2 / obj_dist)
        x = obj_angle / np.tan(self.center.aov / 2) * self.center.width / 2
        y0 = np.average([left_coords[1], right_coords[1]])
        x0, _ = self.center.to_default(x, 0)

        return [int(x0), int(y0), obj_dist]


cam = CameraModel(2048, 1080, np.radians(78))
dcam = DoubleCameraModel(cam, cam, cam, 100)

# User interface

if len(sys.argv) == 1:
    coord_inp = input('Enter coordinates with spaces (xl yl xr yr): ')
    try:
        coords = np.array([int(x) for x in coord_inp.split()]).reshape((2, 2))
        try:
            print(*dcam.obj_coords(*coords))
        except ValueError as error:
            print(error)
    except ValueError:
        print('Entered coordinates must be integer.')

else:
    try:
        data = np.loadtxt(sys.argv[1])
        for i in range(len(data)):
            try:
                print(*dcam.obj_coords(*data[i].reshape(2, 2)))
            except ValueError as error:
                print(error)
    except ValueError as error:
        print(error)
    except OSError as error:
        print(error)
