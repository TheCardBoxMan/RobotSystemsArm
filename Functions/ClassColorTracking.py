import time
import threading
from ArmPi.ArmIK.Transform import *
from ArmPi.ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

# Angle to close the gripper when picking up
servo1 = 500

# Initial position
def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

# Set the RGB light color of the expansion board to match the color being tracked
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()

count = 0
track = False
_stop = False
get_roi = False
center_list = []
first_move = True
__isRunning = False
detect_color = 'None'
action_finish = True
start_pick_up = False
start_count_t1 = True

# Reset variables
def reset():
    global count, track, _stop, get_roi, first_move, center_list, __isRunning, detect_color, action_finish, start_pick_up, start_count_t1
    count = 0
    _stop = False
    track = False
    get_roi = False
    center_list = []
    first_move = True
    detect_color = 'None'
    action_finish = True
    start_pick_up = False
    start_count_t1 = True

# Call for app initialization
def init():
    print("ColorTracking Init")
    initMove()

# Call for app start gameplay
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("ColorTracking Start")

# Call for app stop gameplay
def stop():
    global _stop, __isRunning
    _stop = True
    __isRunning = False
    print("ColorTracking Stop")

# Call for app exit gameplay
def exit():
    global _stop, __isRunning
    _stop = True
    __isRunning = False
    print("ColorTracking Exit")

# Mechanical arm movement thread
def move():
    global track, _stop, get_roi, unreachable, __isRunning, detect_color, action_finish, rotation_angle, world_X, world_Y, world_x, world_y, center_list, count, start_pick_up, first_move

    # Coordinates to place different colored blocks (x, y, z)
    coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }
    while True:
        if __isRunning:
            if first_move and start_pick_up: # When an object is detected for the first time              
                action_finish = False
                set_rgb(detect_color)
                setBuzzer(0.1)               
                result = AK.setPitchRangeMoving((world_X, world_Y - 2, 5), -90, -90, 0) # Adaptively determine running time
                if result == False:
                    unreachable = True
                else:
                    unreachable = False
                time.sleep(result[2]/1000) # The third item in the returned parameter is time
                start_pick_up = False
                first_move = False
                action_finish = True
            elif not first_move and not unreachable: # If not the first time detecting an object
                set_rgb(detect_color)
                if track: # If in tracking phase
                    if not __isRunning: # Check for stop and exit flags
                        continue
                    AK.setPitchRangeMoving((world_x, world_y - 2, 5), -90, -90, 0, 20)
                    time.sleep(0.02)                    
                    track = False
                if start_pick_up: # If the object hasn't moved for a while, start picking up
                    action_finish = False
                    if not __isRunning: # Check for stop and exit flags
                        continue
                    Board.setBusServoPulse(1, servo1 - 280, 500)  # Open the gripper
                    # Calculate the angle the gripper needs to rotate
                    servo2_angle = getAngle(world_X, world_Y, rotation_angle)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    AK.setPitchRangeMoving((world_X, world_Y, 2), -90, -90, 0, 1000)  # Lower the arm
                    time.sleep(2)
                    
                    if not __isRunning:
                        continue
                    Board.setBusServoPulse(1, servo1, 500)  # Close the gripper
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  # Lift the arm
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    # Place different colored blocks
                    result = AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0)   
                    time.sleep(result[2]/1000)
                    
                    if not __isRunning:
                        continue
                    servo2_angle = getAngle(coordinate[detect_color][0], coordinate[detect_color][1], -90)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                    if not __isRunning:
                        continue
                    AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], coordinate[detect_color][2] + 3), -90, -90, 0, 500)
                    time.sleep(0.5)
                    
                    if not __isRunning:
                        continue
                    AK.setPitchRangeMoving((coordinate[detect_color]), -90, -90, 0, 1000)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    Board.setBusServoPulse(1, servo1 - 200, 500)  # Open the gripper, drop the object
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue                    
                    AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0, 800)
                    time.sleep(0.8)

                    initMove()  # Return to the initial position
                    time.sleep(1.5)

                    detect_color = 'None'
                    first_move = True
                    get_roi = False
                    action_finish = True
                    start_pick_up = False
                    set_rgb(detect_color)
                else:
                    time.sleep(0.01)
        else:
            if _stop:
                _stop = False
                Board.setBusServoPulse(1, servo1 - 70, 300)
                time.sleep(0.5)
                Board.setBusServoPulse(2, 500, 500)
                AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                time.sleep(1.5)
            time.sleep(0.01)

# Run the motion control thread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()