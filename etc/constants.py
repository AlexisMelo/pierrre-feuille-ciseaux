### POSTURES ###
PIERRE = "pierre"
FEUILLE = "feuille"
CISEAUX = "ciseaux"
POSSIBLE_GAME_POSTURES = [PIERRE, FEUILLE, CISEAUX]

# Float between 1 included and +inf
# The bigger it is, the wider the user has to open its 2 fingers (index and middle) in order to be recognized as a CISEAUX
# The closer it gets to 1, the smaller the user has to open its 2 fingers in order to be recognized as a CISEAUX
CISEAUX_THRESHOLD = 2

# Float between 0 included and +inf
# The closer it gets to 0, the more stuck the fingers has to be in order to be recognized has a FEUILLE
# The bigger it gets, the less stuck the fingers has to be in order to be recognized has a FEUILLE
# TODO
FEUILLE_THRESHOLD = 0.05

### GESTURES ###
LAUNCH_GAME = "launch_game"
STATISTICS = "statistics"
POSSIBLE_GESTURES = [LAUNCH_GAME, STATISTICS]
# Keep the 10 last images data in memory to detect the gestures
MEMORY_SIZE = 10

### WINNER ###
PLAYER_WIN = "Player"
COMPUTER_WIN = "Computer"

### GAME ###
NB_MAX_ROUND = 5
FRAME_NAME = "Pierre feuille ciseaux"
