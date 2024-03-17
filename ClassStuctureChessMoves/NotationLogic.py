import cv2

def main():
    # Open a video capture device (usually the default webcam)
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Main loop to capture and display frames
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is not captured successfully, break the loop
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Display the captured frame
        cv2.imshow('Video', frame)
        
        
        key = cv2.waitKey(1) & 0xFF

        # Check for the 'q' key press to exit the loop
        if key == ord('q'):
            break

        #





    # Release the video capture object and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


    def pick_place_location(self, location:dict,endlocation:dict, z_offset:float=0.25):
        """Pick the box at a specific coordinate and place it at a choosen location

        Args:
            location (dict): Dictionary with color as key and a tuple of xy and angle as value
            endlocation: (dict): xy location defined
        """

        color = list(location.keys())[0]
        xy = location[color][0]
        angle = location[color][1]

        #Define End Location

        # Home position
        self.home_position()

        # Check if reachable
        result = self.arm.setPitchRangeMoving((xy[0], xy[1], 5), -90, -90, 0)

        if result == False:
            print(f"Box is unreachable at {xy}")
            # Break the function if the box is unreachable
            return

        # Move to top of the box
        self.move_to(xyz=(xy[0], xy[1] + 0.5, 10), move_time=1000)

        # Pick up the box
        self.pick(xy, angle)

        # Place the box
        self.place(color, z_offset)

        # Home position
        self.home_position()

        return
