#!/usr/bin/python3
# coding=utf8

import time
from Utilities import Utils

# Imports from existing ArmPi code
import sys
sys.path.append('/home/pi/RobotSystemsArm/ClassStuctureChessMoves/')
from ArmIK.ArmMoveIK import ArmIK
import HiwonderSDK.Board as Board


class Motion():
    """Class to move the arm to specified coordinates"""

    def __init__(self):

        # Arm instance
        self.arm = ArmIK()

        # Coordinates for keeping back
        self.block_xyz = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        'stack': (-15 + 1, -7 - 0.5, 1.5),
        'orgin': (0,0,1.5)
        }

        # Parameters
        self.gripper_close = 500

        # Utils instance
        self.ut = Utils()

        # Home position
        self.home_position()

        self.RankScale = 4.51
        self.RankOffset = -15.44
        self.FileScale = 4.75
        self.FileOffset = 3.75

    def home_position(self):
        """Move the arm to the home position"""

        Board.setBusServoPulse(1, self.gripper_close -150, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.arm.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(0.5)

    def move_to(self, xyz:tuple, move_time:int=500):
        """Move the arm to specific coordinates"""

        self.arm.setPitchRangeMoving((xyz), -90, -90, 0, move_time)
        time.sleep(2)

    def pick(self, xy:tuple, angle:float):
        """Pick up the box at a specific coordinate"""

        # Open the gripper
        Board.setBusServoPulse(1, self.gripper_close - 280, 500)
        # Rotate the gripper
        servo2_angle = self.ut.getAngle(xy, angle)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)

        # Lower the arm
        self.move_to(xyz=(xy[0], xy[1] + 0.5, 1.5), move_time=1000)

        # Close the gripper
        Board.setBusServoPulse(1, self.gripper_close, 500)
        time.sleep(0.8)

        # Lift the arm
        self.move_to(xyz=(xy[0], xy[1], 12), move_time=1000)

        # Rotate the gripper
        Board.setBusServoPulse(2, 500, 500)
        time.sleep(0.5)

    def place(self, color:str, z_offset:float=0.5):
        """Place the block at coordinates defined by the color

        Args:
            color (str): Color of the block for location
            z_offset (float): Add Offset in height from the block home position
        """

        # Default to red if color not in block_xyz
        if not color in self.block_xyz or color == '':
            color = 'red'

        # Move to top of the block home position
        self.move_to(xyz=(self.block_xyz[color][0], self.block_xyz[color][1], self.block_xyz[color][2] + 12))

        # Rotate the gripper
        servo2_angle = self.ut.getAngle(self.block_xyz[color], -90)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        # Place the block
        place_location = list(self.block_xyz[color])
        place_location[2] += z_offset
        self.move_to(xyz=(place_location), move_time=1000)

        # Open the gripper
        Board.setBusServoPulse(1, self.gripper_close - 200, 500)
        time.sleep(0.8)

        # Lift the arm up
        self.move_to(xyz=(self.block_xyz[color][0], self.block_xyz[color][1], 12), move_time=800)
 

    def place_at_coordinate(self, x: float, y: float, z: float, z_offset: float = 0.5):
        """Place the block at a specified coordinate"""

        # Move to the top of the specified coordinate
        self.move_to(xyz=(x, y, z + 12))

        # Rotate the gripper
        servo2_angle = self.ut.getAngle((x, y), -90)  # Assuming gripper angle is -90
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        # Place the block
        place_location = (x, y, z + z_offset)
        self.move_to(xyz=place_location, move_time=1000)

        # Open the gripper
        Board.setBusServoPulse(1, self.gripper_close - 200, 500)
        time.sleep(0.8)

        # Lift the arm up
        self.move_to(xyz=(x, y, z + 12), move_time=800)

    def pick_and_place_from_chess_notation(self, from_square: str, to_square: str):
        """Pick up a box from a square and place it at another square"""

        # Convert chess notation to Cartesian coordinates
        from_coord = self.convert_chess_to_cartesian(from_square)
        to_coord = self.convert_chess_to_cartesian(to_square)

        if from_coord is None or to_coord is None:
            print("Invalid chess notation.")
            return

        # Pick up the box from the source square
        self.pick(from_coord, angle=0)  # Assuming angle to pick up is 0 degrees

        # Place the box at the destination square
        self.place_at_coordinate(to_coord[0], to_coord[1], 1.5)  # Adjust the height as needed

    def convert_chess_to_cartesian(self, square: str):
        """Convert chess notation to Cartesian coordinates"""


        # Define the mapping from chess notation to Cartesian coordinates
        chess_to_cartesian = {
            'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8
        }

        if len(square) != 2:
            print("Invalid chess notation.")
            return None

        file, rank = square[0], square[1]

        if file not in chess_to_cartesian or not rank.isdigit():
            print("Invalid chess notation.")
            return None

        x = (chess_to_cartesian[file]-1 ) * self.RankScale + self.RankOffset
        y = (int(rank)-1) * self.FileScale + self.FileOffset
             

        #2.6 x and 22.75 is d4
        #7.11 x and 18 y is e3
        #
        return x, y


if __name__ == '__main__':

    # Motion object
    mt = Motion()

    # Test parameters
    color = 'origin'
    xy = (0.0, 20.0)
    angle = -45.0

    # Test pick_place
    mt.pick_place({color: (xy, angle)})