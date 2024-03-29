#!/usr/bin/python3
# coding=utf8

import cv2

from Perception import Perception
from Motion import Motion
from types import SimpleNamespace
from Utilities import Utils

Modes = SimpleNamespace(
    ONE='Pick-Place one box', # Pick and place one box
    SORT='Sort boxes', # Sort all the boxes
    STACK='Stack boxes' # Stack the boxes
)

manual = '''
Color Box Manipulation

Modes:
1: Pick and Place One Box
2: Move Between All
3: Stack the Boxes

Target Color:
r: Red
g: Green
b: Blue

Motion:
c: Execute Motion
q: Quit
'''

def show_info():
    # Clear the screen
    print("\033[H\033[J",end='')
    # Print the manual
    print(manual)

class BoxManip():
    """Class to detect color boxes and manipulate them"""

    def __init__(self):

        # Class instances
        self.perception = Perception()
        self.motion = Motion()

        # Target color - only used in Modes.ONE
        self.target_color = None

        # Mode - Default is pick place one box
        self.mode = Modes.ONE

    def setMode(self, mode:str):
        """Set mode of operation"""
        if mode in Modes.__dict__.values():
            self.mode = mode
        else:
            print(f"Invalid mode: {mode}. Defaulting to Modes.ONE")

    def setTarget(self, color:str):
        """Set target color"""
        self.target_color = color

    def run(self):
        """Run the color box manipulation"""

        show_info()

        # Process image and get the color box locations
        while True:
            img = self.perception.camera.frame

            if img is not None:
                frame = img.copy()
                processed, locations = self.perception.process_image(img=frame)

                cv2.imshow('Processed', processed)
                key = cv2.waitKey(1) & 0xFF

                # Press 'q' to quit
                if key == ord('q'):
                    print("Quitting...")
                    self.motion.home_position()
                    break

                # Change mode with key press
                if key == ord('1'):
                    # Pick and place one box
                    self.setMode(Modes.ONE)
                    print(f"Mode set to {self.mode}")
                elif key == ord('2'):
                    # Sort all the boxes
                    self.setMode(Modes.SORT)
                    print(f"Mode set to {self.mode}")
                elif key == ord('3'):
                    # Stack the boxes
                    self.setMode(Modes.STACK)
                    print(f"Mode set to {self.mode}")

                # Change target color with key press
                if key == ord('r'):
                    self.setTarget('red')
                    print(f"Target color set to {self.target_color}")
                elif key == ord('g'):
                    self.setTarget('green')
                    print(f"Target color set to {self.target_color}")
                elif key == ord('b'):
                    self.setTarget('blue')
                    print(f"Target color set to {self.target_color}")

                # Only proceed if color boxes are detected and 'c' is pressed
                if len(locations) > 0 and key == ord('c'):
                    print(f"Executing motion {self.mode}...")

                    # For Modes.ONE pick place only the target color box
                    if self.mode == Modes.ONE:
                        # Default to Red if target color is not set
                        if self.target_color is None:
                            print("Target color not set. Defaulting to Red")
                            self.target_color = 'red'

                        # If target color is detected, pick and place it
                        if self.target_color in locations:
                            location = {self.target_color: locations[self.target_color]}
                            self.motion.pick_place(location)

                    # For Modes.SORT sort each detected color box one after other
                    elif self.mode == Modes.SORT:
                        self.motion.sort(locations)

                    # For Modes.STACK stack all the detected color boxes
                    elif self.mode == Modes.STACK:
                        self.motion.stack(locations)

                    print("Done Motion...")

        # Close camera and destroy windows
        self.perception.camera.camera_close()
        cv2.destroyAllWindows()


if __name__ == '__main__':

    cb = BoxManip()
    # Run with default mode
    cb.run()