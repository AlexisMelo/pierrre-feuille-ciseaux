import random

import cv2

from etc.constants import FEUILLE, FEUILLE_THRESHOLD, PIERRE, CISEAUX, FRAME_NAME, COMPUTER_WIN, PLAYER_WIN, \
    CISEAUX_THRESHOLD
from src.CustomExceptions import GameInterruptedException
from src.Landmarks import Landmarks, get_landmarks
from src.StatisticsHandler import StatisticsHandler
from src.utils import display_blocking_message_center, display_non_blocking_message_top_left, \
    display_non_blocking_message_bottom_left


class GameHandler:

    def __init__(self, video, player, statistics_handler: StatisticsHandler):
        self.video = video
        self.draw = False
        self.player = player
        self.statistics_handler = statistics_handler

    def initialize_game(self):
        self.statistics_handler.increment_global_stats("games_played")
        number_of_rounds = self.get_number_of_rounds()
        display_blocking_message_center(self.video, f"C'est parti pour {number_of_rounds} rounds !", 25,
                                        font_color=(255, 0, 0))
        self.start_game(number_of_rounds)

    def get_number_of_rounds(self):
        number_of_rounds = 0
        last_gesture = None  # mémoire pour dernière gesture reconnue
        last_gesture_sum = 0  # Nombre de fois qu'on a eu la même gesture d'affilé
        number_of_frames_to_validate = 20
        while last_gesture_sum < number_of_frames_to_validate or not number_of_rounds or number_of_rounds < 1:
            success, frame = self.video.read(0)

            if not success:
                raise RuntimeError("Erreur lecture vidéo pendant l'acquisition du nombre de tours")

            frame = cv2.flip(frame, 1)

            # Faire le traitement et les modifications d'images ici
            # Landmarks' keypoints coordinates (0,0) is top left, (1,1) is bottom right
            frame, landmarks = get_landmarks(frame, self.draw)
            number_of_rounds = self.recognize_number_of_rounds_posture(landmarks)

            if number_of_rounds == last_gesture:
                last_gesture_sum += 1
            else:
                last_gesture_sum = 0

            if number_of_rounds:
                display_non_blocking_message_bottom_left(frame, f"{last_gesture_sum} / {number_of_frames_to_validate}")

            last_gesture = number_of_rounds

            display_non_blocking_message_top_left(frame, f"Nombre de rounds : {number_of_rounds}")

            cv2.imshow(FRAME_NAME, frame)

            key = cv2.pollKey() & 0xFF
            if key == ord("d"):
                self.draw = not self.draw
            elif key == ord("q"):
                raise GameInterruptedException

        self.statistics_handler.increment_global_stats("rounds_expected_to_be_played", number_of_rounds)
        return number_of_rounds

    def recognize_number_of_rounds_posture(self, landmarks: Landmarks):
        """
        Return the number of stretched fingers corresponding to the numbers of rounds.

        The hand has to be correctly oriented (top of fingers towards the
        top of the image from woth the landmarks has been extracted).
        Works if it's either the hand palm facing the camera or the back of the hand.

        If the landmarks object attribute containing the keypoints is None,
        (i.e. no hand detected) the function returns None.

        Parameters
        ----------
        landmarks -- The landmarks object of the hand for which we want to count the fingers

        Return
        ------
        an int -- the number of stretched fingers
        """

        if not landmarks.is_not_none():
            return None

        # Determine if it's the palm or the back that is facing the camera
        # in order to choose the condition determining if the thumb is stretched or not
        palm_facing_camera = landmarks.get_keypoint_x(5) < landmarks.get_keypoint_x(17)

        if palm_facing_camera:
            thumb_up = landmarks.get_keypoint_x(4) < landmarks.get_keypoint_x(2)
        else:
            thumb_up = landmarks.get_keypoint_x(4) > landmarks.get_keypoint_x(2)

        index_up = landmarks.get_keypoint_y(8) < landmarks.get_keypoint_y(6)
        middle_up = landmarks.get_keypoint_y(12) < landmarks.get_keypoint_y(10)
        ring_up = landmarks.get_keypoint_y(16) < landmarks.get_keypoint_y(14)
        pinky_up = landmarks.get_keypoint_y(20) < landmarks.get_keypoint_y(18)
        return thumb_up + index_up + middle_up + ring_up + pinky_up

    def get_user_posture(self):
        last_gesture = None  # mémoire pour dernière gesture reconnue
        posture_player = None
        last_gesture_sum = 0  # Nombre de fois qu'on a eu la même gesture d'affilé
        number_of_frames_to_validate = 20

        while last_gesture_sum < number_of_frames_to_validate:

            success, frame = self.video.read(0)

            if not success:
                print("Erreur lecture vidéo pendant l'acquisition de la posture")
                break

            frame = cv2.flip(frame, 1)

            # Faire le traitement et les modifications d'images ici
            # Landmarks' keypoints coordinates (0,0) is top left, (1,1) is bottom right
            frame, landmarks = get_landmarks(frame, self.draw)

            posture_player = self.recognize_user_game_posture(landmarks)

            if posture_player == last_gesture and posture_player is not None:
                last_gesture_sum += 1
            else:
                last_gesture_sum = 0

            if posture_player is not None:
                display_non_blocking_message_bottom_left(frame,
                                                         f"{last_gesture_sum} / {number_of_frames_to_validate}")

            last_gesture = posture_player

            display_non_blocking_message_top_left(frame, f"Posture detectee : {posture_player}")

            cv2.imshow(FRAME_NAME, frame)

            key = cv2.pollKey() & 0xFF
            if key == ord("d"):
                self.draw = not self.draw
            if key == ord("q"):
                raise GameInterruptedException

        return posture_player

    def recognize_user_game_posture(self, landmarks: Landmarks):
        """
        Return the symbol made by the hand on the image
        which is an element of POSSIBLE_GAME_POSTURES.

        Parameters
        ----------
        landmarks -- The landmarks object of the hand for which we want to recognize the posture

        Return
        ------
        a String -- The recognized game posture (CISEAUX, PIERRE or FEUILLE) or None if 
            no game posture is recognized
        """

        if not landmarks.is_not_none():
            return None

        # The posture is a CISEAUX if the space between keypoint 8 and 12 
        # is wider than the space between 5 and 9
        # and if ring and pinky fingers aren't stretched
        distance_top_fingers = landmarks.get_distance_between(8, 12)
        distance_bottom_fingers = landmarks.get_distance_between(5, 9)
        ring_down = landmarks.get_keypoint_y(16) > landmarks.get_keypoint_y(14)
        pinky_down = landmarks.get_keypoint_y(20) > landmarks.get_keypoint_y(18)
        is_ciseaux = ring_down and pinky_down and distance_top_fingers > CISEAUX_THRESHOLD * distance_bottom_fingers
        if is_ciseaux:
            return CISEAUX

        # The posture is a PIERRE if is all fingers aren't stretched
        # (i.e. if this were the posture to determine the nb of rounds, the result would be 0)
        is_pierre = self.recognize_number_of_rounds_posture(landmarks) == 0
        if is_pierre:
            return PIERRE

        # The posture is a FEUILLE if the distance between keypoint 6 and 19 is close to 5 and 17
        distance_stuck_fingers1 = landmarks.get_distance_between(6, 19)
        distance_stuck_fingers2 = landmarks.get_distance_between(5, 17)
        is_feuille = distance_stuck_fingers1 - distance_stuck_fingers2 < FEUILLE_THRESHOLD
        if is_feuille:
            return FEUILLE

        # Return None if no game posture has been recognized
        return None

    def start_game(self, number_of_rounds):
        rounds_played = 0
        player_rounds_won = 0
        computer_rounds_won = 0
        while rounds_played < number_of_rounds:

            posture_player, posture_computer = self.get_round_postures(rounds_played, number_of_rounds)

            winner = self.get_winner(posture_player, posture_computer)

            if winner == PLAYER_WIN:
                display_blocking_message_center(self.video,
                                                f"Bravo ! Tu remportes le round ({posture_player} > {posture_computer})",
                                                25,
                                                font_size=1,
                                                font_stroke=2)
                player_rounds_won = player_rounds_won + 1
            elif winner == COMPUTER_WIN:
                display_blocking_message_center(self.video,
                                                f"Dommage, l'ordinateur remporte le round ({posture_computer} > {posture_player})",
                                                25,
                                                font_size=1,
                                                font_stroke=2)
                computer_rounds_won = computer_rounds_won + 1
            else:
                display_blocking_message_center(self.video, f"Match nul ! Aucun gagnant ce round", 25)

            rounds_played = rounds_played + 1
            self.statistics_handler.increment_global_stats("rounds_played")

            key = cv2.pollKey() & 0xFF
            if key == ord("q"):
                raise GameInterruptedException

        if player_rounds_won > computer_rounds_won:
            display_blocking_message_center(self.video,
                                            f"Victoire {player_rounds_won} rounds a {computer_rounds_won} !", 50,
                                            font_color=(0, 255, 0))
            self.statistics_handler.increment_stats_player(self.player, "games_won")
        elif computer_rounds_won > player_rounds_won:
            display_blocking_message_center(self.video,
                                            f"Defaite {player_rounds_won} rounds a {computer_rounds_won} ...", 50,
                                            font_color=(0, 0, 255))
            self.statistics_handler.increment_stats_player("computer", "games_won")
        else:
            display_blocking_message_center(self.video,
                                            f"Egalite ! Aucun gagnant cette fois-ci...",
                                            50,
                                            font_color=(255, 0, 0))
            self.statistics_handler.increment_global_stats("games_even")

        self.log_rounds_to_stats(self.player, player_rounds_won, computer_rounds_won, rounds_played)
        self.log_rounds_to_stats("computer", player_rounds_won, computer_rounds_won, rounds_played)

    def log_rounds_to_stats(self, player, player_rounds_won, computer_rounds_won, rounds_played):
        self.statistics_handler.increment_stats_player(player, "rounds_won", player_rounds_won)
        self.statistics_handler.increment_stats_player(player, "rounds_lost", computer_rounds_won)
        self.statistics_handler.increment_stats_player(player, "rounds_even",
                                                       rounds_played - player_rounds_won - computer_rounds_won)

    def get_round_postures(self, rounds_played, number_of_rounds):
        display_blocking_message_center(self.video, f"Round {rounds_played + 1} / {number_of_rounds}", 25,
                                        font_color=(255, 0, 0))

        posture_player = self.get_user_posture()

        display_blocking_message_center(self.video, f"Acquisition humain : {posture_player}", 15)

        posture_computer = self.get_computer_game_posture()

        display_blocking_message_center(self.video, f"Posture ordi : {posture_computer}", 25)

        self.statistics_handler.increment_stats_player("computer", posture_computer)
        self.statistics_handler.increment_stats_player(self.player, posture_player)

        return posture_player, posture_computer

    def get_computer_game_posture(self):
        return random.choice([FEUILLE, PIERRE, CISEAUX])

    def get_winner(self, posture_player, posture_computer):
        if posture_computer == posture_player:
            return None

        better_posture = self.get_better_posture(posture_player)

        if posture_computer == better_posture:
            return COMPUTER_WIN

        return PLAYER_WIN

    def get_better_posture(self, posture):
        if posture == FEUILLE:
            return CISEAUX

        if posture == PIERRE:
            return FEUILLE

        return PIERRE
