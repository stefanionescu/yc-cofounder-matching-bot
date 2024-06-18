from time import sleep
from random import randint
import constants as CONSTANTS

class Utils:
    def __init__(self):
        return

    def random_short_sleep(min=CONSTANTS.SHORT_MIN_SECONDS_TO_WAIT, max=CONSTANTS.SHORT_MAX_SECONDS_TO_WAIT):
        sleep(randint(min, max))

    def random_normal_sleep(min=CONSTANTS.NORMAL_MIN_SECONDS_TO_WAIT, max=CONSTANTS.NORMAL_MAX_SECONDS_TO_WAIT):
        sleep(randint(min, max))

    def random_long_sleep(min=CONSTANTS.LONG_MIN_SECONDS_TO_WAIT, max=CONSTANTS.LONG_MAX_SECONDS_TO_WAIT):
        sleep(randint(min, max))