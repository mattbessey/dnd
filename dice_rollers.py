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


def roll_dice(die: list):
    """
    rolls dice of type [number, type]
    e.g., 3d6 = [3, 6]
    """
    return sum([random.randint(1, die[1]) for _ in range(die[0])])
