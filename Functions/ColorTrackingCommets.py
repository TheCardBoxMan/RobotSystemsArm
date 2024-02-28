#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

#__target_color = ('blue')
# 设置检测颜色
def setTargetColor(target_color):
    global __target_color

    #print("COLOR", target_color)
    __target_color = target_color
    return (True, ())

# 找出面积最大的轮廓
# 参数为要比较的轮廓的列表
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓

# 夹持器夹取时闭合的角度
servo1 = 500

# 初始位置
def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

#设置扩展板的RGB灯颜色使其跟要追踪的颜色一致
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
# 变量重置
def reset():
    global count
    global track
    global _stop
    global get_roi
    global first_move
    global center_list
    global __isRunning
    global detect_color
    global action_finish
    global start_pick_up
    global __target_color
    global start_count_t1
    
    count = 0
    _stop = False
    track = False
    get_roi = False
    center_list = []
    first_move = True
    __target_color = ()
    detect_color = 'None'
    action_finish = True
    start_pick_up = False
    start_count_t1 = True

# app初始化调用
def init():
    print("ColorTracking Init")
    initMove()

# app开始玩法调用
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("ColorTracking Start")

# app停止玩法调用
def stop():
    global _stop 
    global __isRunning
    _stop = True
    __isRunning = False
    print("ColorTracking Stop")

# app退出玩法调用
def exit():
    global _stop
    global __isRunning
    _stop = True
    __isRunning = False
    print("ColorTracking Exit")

rect = None
size = (640, 480)
rotation_angle = 0
unreachable = False
world_X, world_Y = 0, 0
world_x, world_y = 0, 0
# 机械臂移动线程
def move():
    global rect
    global track
    global _stop
    global get_roi
    global unreachable
    global __isRunning
    global detect_color
    global action_finish
    global rotation_angle
    global world_X, world_Y
    global world_x, world_y
    global center_list, count
    global start_pick_up, first_move

    # 不同颜色木快放置坐标(x, y, z)
    coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }
    while True:
        if __isRunning:
            if first_move and start_pick_up: # 当首次检测到物体时               
                action_finish = False
                set_rgb(detect_color)
                setBuzzer(0.1)               
                result = AK.setPitchRangeMoving((world_X, world_Y - 2, 5), -90, -90, 0) # 不填运行时间参数，自适应运行时间
                if result == False:
                    unreachable = True
                else:
                    unreachable = False
                time.sleep(result[2]/1000) # 返回参数的第三项为时间
                start_pick_up = False
                first_move = False
                action_finish = True
            elif not first_move and not unreachable: # 不是第一次检测到物体
                set_rgb(detect_color)
                if track: # 如果是跟踪阶段
                    if not __isRunning: # 停止以及退出标志位检测
                        continue
                    AK.setPitchRangeMoving((world_x, world_y - 2, 5), -90, -90, 0, 20)
                    time.sleep(0.02)                    
                    track = False
                if start_pick_up: #如果物体没有移动一段时间，开始夹取
                    action_finish = False
                    if not __isRunning: # 停止以及退出标志位检测
                        continue
                    Board.setBusServoPulse(1, servo1 - 280, 500)  # 爪子张开
                    # 计算夹持器需要旋转的角度
                    servo2_angle = getAngle(world_X, world_Y, rotation_angle)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue
                    AK.setPitchRangeMoving((world_X, world_Y, 2), -90, -90, 0, 1000)  # 降低高度
                    time.sleep(2)
                    
                    if not __isRunning:
                        continue
                    Board.setBusServoPulse(1, servo1, 500)  # 夹持器闭合
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  # 机械臂抬起
                    time.sleep(1)
                    
                    if not __isRunning:
                        continue
                    # 对不同颜色方块进行分类放置
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
                    Board.setBusServoPulse(1, servo1 - 200, 500)  # 爪子张开，放下物体
                    time.sleep(0.8)
                    
                    if not __isRunning:
                        continue                    
                    AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0, 800)
                    time.sleep(0.8)

                    initMove()  # 回到初始位置
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

# 运行子线程
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

t1 = 0
roi = ()
last_x, last_y = 0, 0

# Function to perform perception tasks on the input image
class Perception:
    def __init__(self,__target_color):
        self.__target_color = __target_color
        # Initialize variables
        self.roi = None
        self.rect = None
        self.count = 0
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.__isRunning = False
        self.unreachable = False
        self.detect_color = None
        self.action_finish = False
        self.rotation_angle = None
        self.last_x, self.last_y = 0, 0
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.start_count_t1, self.t1 = False, 0
        self.start_pick_up, self.first_move = False, False

        # Initialize variables for contour detection
        self.area_max = 0
        self.areaMaxContour = 0

        
    #Draws the lines and Gets a color space image
    def CopyImage(self,img):

        # Make a copy of the input image
        self.img = img
        self.img_copy = img.copy()
        self.img_h, self.img_w = img.shape[:2]
    
    def Calibation_Lines(self):
        # Draw horizontal and vertical lines on the image
        cv2.line(img, (0, int(self.img_h / 2)), (self.img_w, int(self.img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(self.img_w / 2), 0), (int(self.img_w / 2), self.img_h), (0, 0, 200), 1)
    
    def Check_Running(self):
        # Check if the program is running
        if not self.__isRunning:
            return img
        
    def Resize(self):
        # Resize the image to a predefined size
        self.frame_resize = cv2.resize(self.img_copy, size, interpolation=cv2.INTER_NEAREST)
        
    def Gaussian_Blur(self):
        #apply Gaussian blur
        self.frame_gb = cv2.GaussianBlur(self.frame_resize, (11, 11), 11)

    
    #Get a part of the frame and convert color
    def Gather_Frame(self):
        # If an object is detected in a specific region of interest, continue tracking it
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            self.frame_gb = getMaskROI(self.frame_gb, self.roi, size)    
    def Covert_to_LAB_Color(self):
        # Convert the image to LAB color space
        self.frame_lab = cv2.cvtColor(self.frame_gb, cv2.COLOR_BGR2LAB)

    def IterateColorRanges(self):
        # Iterate through predefined color ranges
        for i in color_range:
            if i in self.__target_color:
                detect_color = i
                # Create a mask based on the detected color range
                frame_mask = cv2.inRange(self.frame_lab, color_range[detect_color][0], color_range[detect_color][1])

                # Perform morphological operations to remove noise
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))

                # Find contours in the masked image
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
                
                # Get the largest contour
                self.areaMaxContour, self.area_max = getAreaMaxContour(contours)
    
    
    def min_bounding_rec(self):
        # Get the minimum bounding rectangle of the contour
        self.rect = cv2.minAreaRect(self.areaMaxContour)
        self.box = np.int0(cv2.boxPoints(self.rect))

    def Perceive_Blocks(self,img):

        P.CopyImage(img)
        P.Calibation_Lines()
        P.Check_Running()
        P.Resize()
        P.Gaussian_Blur()
        P.Gather_Frame()
        P.Covert_to_LAB_Color()
        # If not in the process of picking up an object
        if not self.start_pick_up:
            P.IterateColorRanges()
            # Iterate through predefined color ranges

            # If a large enough contour is found
            if self.area_max > 2500:
                P.min_bounding_rec()
                # Get the minimum bounding rectangle of the contour

                # Get the region of interest (ROI) based on the bounding box
                self.roi = getROI(self.box)
                self.get_roi = True

                # Calculate the center coordinates of the object in the image
                self.img_centerx, self.img_centery = getCenter(self.rect, self.roi, size, square_length)
                # Convert image coordinates to real-world coordinates
                self.world_x, self.world_y = convertCoordinate(self.img_centerx, self.img_centery, size)
                
                # Draw contour and center point on the image
                cv2.drawContours(self.img, [self.box], -1, range_rgb[detect_color], 2)
                cv2.putText(self.img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(self.box[0, 0], self.box[2, 0]), self.box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1)
                
                # Calculate distance between current and previous coordinates
                distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2))
                last_x, last_y = world_x, world_y
                self.track = True
                
                # If the action is finished, update arm movements
                if action_finish:
                    if distance < 0.3:
                        # Accumulate coordinates for object tracking
                        center_list.extend((world_x, world_y))
                        count += 1
                        if self.start_count_t1:
                            self.start_count_t1 = False
                            self.t1 = time.time()
                        if time.time() - self.t1 > 1.5:
                            self.rotation_angle = self.rect[2]
                            self.start_count_t1 = True
                            self.world_X, self.world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                            count = 0
                            center_list = []
                            self.start_pick_up = True
                    else:
                        self.t1 = time.time()
                        self.start_count_t1 = True
                        count = 0
                        center_list = []
                        
        return self.img



if __name__ == '__main__':
    init()
    start()
    __target_color = ('green',)
    P = Perception(__target_color)

    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()

            #New Perception Code
            Frame = P.Perceive_Blocks(img)

            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
