import cv2
import mediapipe as mp
import math # Import math module for hypot function

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        # CORRECTED LINE: Pass arguments as keyword arguments
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        # CORRECTED LINE: Initialize tipIds for fingersUp method
        self.tipIds = [4, 8, 12, 16, 20] # IDs for the tips of thumb, index, middle, ring, pinky fingers

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        # Initialize bbox with default values in case no hands are detected
        self.bbox = (0, 0, 0, 0)
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            x_coords = []
            y_coords = []
            for id, lm in enumerate(myHand.landmark):
                # print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                x_coords.append(cx)
                y_coords.append(cy)

            # Calculate bounding box using min/max of all landmarks
            x_min, y_min = min(x_coords), min(y_coords)
            x_max, y_max = max(x_coords), max(y_coords)
            self.bbox = (x_min, y_min, x_max - x_min, y_max - y_min)

            if draw:
                # Unpack bbox values for drawing rectangle
                bx, by, bw, bh = self.bbox
                cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (255, 0, 255), 2)

        return self.lmList, self.bbox

    def fingersUp(self):
        fingers = []
        if self.lmList:
            # Thumb
            # Compare x coordinate for thumb (tip 4) with the base (point 3) for right hand
            # For left hand, it might be reversed, but typical examples check x-axis for thumb
            # A more robust check might involve checking distance from wrist or a fixed point.
            # Assuming right hand for typical thumb movement detection
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]: # Check X-coord (assuming thumb moves right for 'up')
                fingers.append(1)
            else:
                fingers.append(0)

            # 4 Fingers (Index, Middle, Ring, Pinky)
            # Compare y coordinate of tip with the y coordinate of the knuckle below it
            for id in range(1, 5): # Iterate from index finger (id 1 in tipIds) to pinky (id 4)
                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]: # Check Y-coord (tip is higher)
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        if len(self.lmList) != 0: # Check if lmList is not empty
            x1, y1 = self.lmList[p1][1:]
            x2, y2 = self.lmList[p2][1:]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if draw:
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
            length = math.hypot(x2 - x1, y2 - y1)
            return length, img, [x1, y1, x2, y2, cx, cy]
        return 0, img, [0,0,0,0,0,0] # Return default values if no landmarks

def main():
    cap = cv2.VideoCapture(0) # Changed to 0 for default camera
    detector = handDetector()
    pTime = 0 # Previous time for FPS calculation
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if len(lmList) != 0:
            # print(lmList[8]) # Example: print tip of index finger
            fingers = detector.fingersUp()
            # print(fingers)
            length, img, lineInfo = detector.findDistance(8, 12, img) # Distance between index and middle
            # print(length)

        # Calculate and display FPS
        cTime = time.time() # Current time
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import time # Import time for main function
    main()