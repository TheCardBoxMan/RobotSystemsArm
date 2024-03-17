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
