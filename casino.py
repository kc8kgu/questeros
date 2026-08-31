"""Pure rules for town casino Double-or-Nothing."""
import random

BET_AMOUNTS = (10, 25, 50, 100)
CASINO_ALERT_GOLD = 200


def flip():
    return random.random() < 0.5
