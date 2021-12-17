import cv2
import numpy as np
import image_utils as iu
import detection_utils as du
from constants import *


def run_app():
    # define a video capture object (0 = default webcam)
    vid = cv2.VideoCapture(0)
    while True:
        # Capture the video frame by frame
        ret, frame = vid.read(0)

        # Faire le traitement et les modifications d'images ici
        # e.g. : frame = iu.write_score(frame)
        start_gesture = get_starting_gesture()
        if start_gesture == LAUNCH_GAME:
            nb_rounds = get_number_of_rounds_posture()
            cpt = 0
            while(cpt < nb_rounds):
                posture_player = get_user_game_posture()
                posture_computer = get_computer_game_posture()
                display_computer_game_posture()
                winner = get_winner(posture_player, posture_computer)
                display_winner_or_round(winner)
                #mettre un sleeep pour laisser afficher le score quelques 
                #secondes et empecher les interations
                cpt += 1
            display_final_winner()
        elif start_gesture == STATISTICS:
            display_scores_previous_games()


        # Display the resulting frame
        cv2.imshow("frame", frame)

        # Press 'q' to quit
        key = cv2.pollKey() & 0xFF
        if key == ord("q"):
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

def get_winner(posture_player, posture_computer):
    win_gesture = get_gesture_winner(posture_player, posture_computer)
    if win_gesture == posture_player:
        return PLAYER_WIN
    else:
        return COMPUTER_WIN
    
def get_gesture_winner(g1,g2):
    if (g1 == CISEAUX and g2 == PIERRE) or (g2 == CISEAUX and g1 == PIERRE):
        return PIERRE
    elif (g1 == CISEAUX and g2 == FEUILLE) or (g2 == CISEAUX and g1 == FEUILLE):
        return CISEAUX
    elif (g1 == PIERRE and g2 == FEUILLE) or (g2 == PIERRE and g1 == FEUILLE):
        return FEUILLE

if __name__ == "__main__":
    print "main"