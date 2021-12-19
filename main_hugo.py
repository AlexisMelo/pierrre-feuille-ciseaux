import cv2
import numpy as np
from ImageMemory import ImageMemory
import image_utils as iu
import detection_utils as du
from constants import *
import mediapipe as mp


def run_app():
    # define a video capture object (0 = default webcam)
    vid = cv2.VideoCapture(0)
    im = ImageMemory(memory_size=10)
    i = 1

    while True:
        # Capture the video frame by frame
        ret, frame = vid.read(0)

        # Faire le traitement et les modifications d'images ici
        # e.g. : frame = iu.write_score(frame)
        # frame, dico = du.get_landmarks(frame, draw=True)
        im.add(frame)
        if im.recognize_start_gesture() == LAUNCH_GAME:
            i += 1
            print("SWIPE ", i)

        # Display the resulting frame
        cv2.imshow("frame", cv2.flip(frame, 1))

        # Press 'q' to quit
        key = cv2.pollKey() & 0xFF
        if key == ord("q"):
            # print(dico)
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_app()
