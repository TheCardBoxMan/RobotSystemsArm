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

        # Check for key press
        key = cv2.waitKey(1) & 0xFF

        # If 'q' key is pressed, quit the program
        if key == ord('q'):
            break
        
        # If left mouse button is clicked, print chess notation of coordinates
        if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) >= 1 and cv2.getWindowProperty('Video', cv2.WND_PROP_AUTOSIZE) >= 1:
            if cv2.waitKey(1) == ord('c'):
                x, y = cv2.waitKey(0) & 0xFF, cv2.waitKey(0) & 0xFF
                print(f"Chess Notation: {chr(ord('a') + x // 64)}{8 - y // 64}")
    
    # Release the video capture object and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()