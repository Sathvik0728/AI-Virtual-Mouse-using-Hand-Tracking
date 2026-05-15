import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

#####################################
wCam, hCam = 640, 480
frameR = 100 # Frame Reduction (defines the active region for mouse control)
smoothening = 7 # Smoothening factor for mouse movement
#####################################

pTime = 0 # Previous time for calculating FPS
plocX, plocY = 0, 0 # Previous location of the mouse cursor
clocX, clocY = 0, 0 # Current location of the mouse cursor

# Initialize webcam (use 0 for your default camera, or try 1 if 0 doesn't work)
cap = cv2.VideoCapture(0)
cap.set(3, wCam) # Set camera width
cap.set(4, hCam) # Set camera height

# Initialize the hand detector to track a maximum of one hand
detector = htm.handDetector(maxHands=1)

# Get the dimensions of your computer screen using autopy
wScr, hScr = autopy.screen.size()

while True:
    # 1. Read a frame from the webcam
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from camera. Exiting...")
        break # Exit the loop if camera read fails

    # Flip the image horizontally for a natural mirror effect, matching how you see your hand
    img = cv2.flip(img, 1)

    # Find hands in the image and draw landmarks
    img = detector.findHands(img)
    # Get the list of hand landmarks (lmList) and the bounding box (bbox) around the hand
    lmList, bbox = detector.findPosition(img, draw=True) # draw=True will draw the bounding box

    # 2. Proceed only if hand landmarks are detected in the current frame
    if len(lmList) != 0:
        # Get the coordinates of the tip of the index finger (landmark ID 8)
        x1, y1 = lmList[8][1], lmList[8][2]
        # Get the coordinates of the tip of the middle finger (landmark ID 12)
        x2, y2 = lmList[12][1], lmList[12][2]

        # 3. Determine which fingers are currently up
        # This returns a list where 1 means finger is up, 0 means down (e.g., [thumb, index, middle, ring, pinky])
        fingers = detector.fingersUp()

        # Draw the rectangle indicating the active mouse control area on the screen
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # 4. Moving Mode: Check if only the Index Finger is up (and Middle Finger is down)
        # fingers[1] is the Index finger, fingers[2] is the Middle finger
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates: Map the index finger's position from camera frame to screen resolution
            # np.interp scales the value from one range to another
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 6. Smoothen Mouse Movement: Reduce jerky movements by averaging current and previous positions
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse: Use autopy to move the mouse cursor
            # The flipped image usually means you can use clocX directly without wScr - clocX
            autopy.mouse.move(clocX, clocY)
            # Draw a filled circle at the index finger tip in the camera feed
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            # Update the previous mouse location for the next frame
            plocX, plocY = clocX, clocY

        # 8. Clicking Mode: Check if both Index and Middle Fingers are Up
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between the Index and Middle fingers
            # This helps detect a "pinch" gesture for clicking
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # print(length) # Debugging: print the distance

            # 10. Click Mouse: If the distance is below a threshold (fingers are pinched)
            if length < 40: # This threshold can be adjusted based on preference
                # lineInfo contains coordinates [x1, y1, x2, y2, cx, cy]
                # cx, cy are the center coordinates between the two finger tips
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED) # Draw green circle at pinch point
                autopy.mouse.click() # Perform a mouse click

    # 11. Calculate and Display Frame Rate (FPS)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display the processed camera feed in a window
    cv2.imshow("AI Virtual Mouse", img)

    # 13. Wait for a key press (1ms delay) and exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows when the loop ends
cap.release()
cv2.destroyAllWindows()