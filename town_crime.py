"""Pure rules for town vendor crime and guard combat."""
import random

ROB_GOLD_MIN = 10
ROB_GOLD_MAX = 40

VENDOR_MONSTER = dict(
    id="goblin", name="Vendor", hp=12, atk=4, dfn=1, gold=30, xp=10)
GUARD_MONSTER = dict(
    id="skeleton", name="Guard", hp=20, atk=7, dfn=3, gold=15, xp=20)


def rob_gold():
    return random.randint(ROB_GOLD_MIN, ROB_GOLD_MAX)
