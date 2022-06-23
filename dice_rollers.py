# import stuff
import numpy as np
import random
import math


def statsRoller() -> int:
    """
    Rolls 4d6, drops lowest, returns sum
    """
    roll_list = [random.randint(1, 6) for _ in range(4)]
    roll_list.remove(min(roll_list))
    return sum(roll_list)


def rollSixStats() -> list:
    """
    Rolls 6 stats and returns the list
    """
    return [statsRoller() for _ in range(6)]


def findStatModifier(stat: int) -> int:
    """
    Finds the modifier for a given stat value
    """
    return math.floor((stat - 10) / 2)


def roll_dice(number, die_type):
    return sum([random.randint(1, die_type) for _ in range(number)])
