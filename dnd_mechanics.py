from dice_rollers import rollSixStats, findStatModifier, roll_dice
import itertools
import statistics
import random
import pandas as pd
import numpy as np


class Weapon(object):
    def __init__(
        self, damage_die: list = [1, 6], statistic: str = "str", modifier: int = 0
    ):
        self.damage_die = damage_die
        self.statistic = statistic
        self.modifier = modifier

    def deal_damage(self, is_crit: bool = False):
        if is_crit:
            return roll_dice(self.damage_die) + roll_dice(self.damage_die) + self.modifier
        else:
            return roll_dice(self.damage_die) + self.modifier


class Character(object):
    def __init__(self, name: str, hit_die: list = [1, 10], stat_list: list =
                 ["str", "dex", "con", "int", "wis", "cha"]):
        self.name = name
        self.hit_die = hit_die
        self.state = "alive"
        self.armor_class = 15
        self.initiative = 0
        self.stat_list = stat_list
        self.level = 1
        self.weapon = Weapon(damage_die=[1, 1])
        self.hitpoints = 0
        self.max_hitpoints = 0

        # set attributes
        self.str = self.dex = self.con = self.int = self.wis = self.cha = 0

        # I don't actually know if this is good practice
        self.get_stat_mod = findStatModifier

    def set_stat(self, stat_to_modify: str, stat_number: int):
        setattr(self, stat_to_modify, stat_number)

    def set_hitpoints(self):
        # first level shouldn't have a roll
        con_mod = self.get_stat_mod(self.con)
        self.max_hitpoints = roll_dice(
            self.hit_die) + (con_mod * self.hit_die[0]) + self.hit_die[1]

    def get_attacked(self, attack_dictionary: dict):

        if attack_dictionary["to_hit"] >= self.armor_class:
            self.take_damage(attack_dictionary["damage"])

    def take_damage(self, damage: int):
        if damage >= self.hitpoints:
            self.state = "dead"
        self.hitpoints -= damage

    def equip_weapon(self, weapon: Weapon):
        self.weapon = weapon

    def attack(self, attack_stat: int = "str") -> dict:
        modifier = self.get_stat_mod(getattr(self, attack_stat))

        roll = roll_dice([1, 20])

        to_hit = roll + modifier

        if roll == 20:
            damage = self.weapon.deal_damage(is_crit=True)
        else:
            damage = self.weapon.deal_damage(is_crit=False)

        damage += modifier

        return {"to_hit": to_hit, "damage": damage}

    def roll_for_initiative(self):
        self.initiative = roll_dice([1, 20]) + self.get_stat_mod(self.dex)

    def change_hitpoints(self, amount: int = 0):
        self.hitpoints += amount

    def reset_hitpoints(self):
        self.hitpoints = self.max_hitpoints


def create_character(stat_list: list, stat_rank_order: list, name: str = "random_character") -> Character:
    """
    Creates a Character with given name.
    Stats are taken from stat_list and assigned
    in descending rank order based on stat_rank_order
    """
    stat_list.sort(reverse=True)
    character = Character(name, stat_list=stat_list)
    for i in range(len(stat_rank_order)):
        character.set_stat(
            stat_to_modify=stat_rank_order[i], stat_number=stat_list[i])
    character.set_hitpoints()
    return character


def create_character_easy(name: str) -> Character:
    """
    Creates a character given just a string for a name
    """
    stat_list = rollSixStats()
    stat_rank_order = ["dex", "str", "int", "con", "cha", "wis"]
    random.shuffle(stat_rank_order)
    character = create_character(
        name=name, stat_list=stat_list, stat_rank_order=stat_rank_order
    )
    katana = Weapon()
    character.equip_weapon(katana)

    return character


def create_all_character_variations(stat_rolls: list = None):
    """
    Creates character for each permutation of stat orders.
    Can either take a fixed list of stat rolls or
    Generate stats for each character randomly
    """
    stat_list = ["str", "dex", "con", "int", "wis", "cha"]
    permutations = list(itertools.permutations(stat_list))
    generated_characters = []

    if stat_rolls:
        for i in range(len(permutations)):
            name = "character_" + str(i)
            character = create_character(
                name=name, stat_rank_order=permutations[i], stat_list=stat_rolls)
            generated_characters.append(character)
    else:
        for i in range(len(permutations)):
            name = "character_" + str(i)
            stat_rolls = rollSixStats()
            character = create_character(
                name=name, stat_rank_order=permutations[i], stat_list=stat_rolls)
            generated_characters.append(character)

    return generated_characters


def fight_to_death(character1: Character, character2: Character):
    character1.hitpoints = character1.max_hitpoints
    character2.hitpoints = character2.max_hitpoints
    character1.roll_for_initiative()
    character2.roll_for_initiative()
    turn_count = 0
    character1_attacks = []
    character2_attacks = []

    if character1.initiative > character2.initiative:
        while character1.state == "alive" and character2.state == "alive":
            turn_count += 1

            attack = character1.attack()
            character1_attacks.append(attack)
            character2.get_attacked(attack)

            attack = character2.attack()
            character2_attacks.append(attack)
            character1.get_attacked(attack)

    elif character2.initiative > character1.initiative:
        while character1.state == "alive" and character2.state == "alive":
            turn_count += 1

            attack = character2.attack()
            character2_attacks.append(attack)
            character1.get_attacked(attack)

            attack = character1.attack()
            character1_attacks.append(attack)
            character2.get_attacked(attack)

    if character1.state == "alive":
        return {
            "winner": character1,
            "loser": character2,
            "turn_count": turn_count,
            "character1_attacks": character1_attacks,
            "character2_attacks": character2_attacks
        }

    elif character2.state == "alive":
        return {
            "winner": character2,
            "loser": character1,
            "turn_count": turn_count,
            "character1_attacks": character1_attacks,
            "character2_attacks": character2_attacks
        }

    else:
        return {
            "winner": None,
            "loser": None,
            "turn_count": turn_count,
            "character1_attacks": character1_attacks,
            "character2_attacks": character2_attacks
        }


def summarize_character_list(character_list: list,
                             stats_to_analyze: list = ["level", "hitpoints", "str",
                                                       "dex", "con", "int", "wis", "cha"]) -> dict:
    """
    Takes a list of characters and summarizes their stats.
    """
    stat_dict = {}

    for _ in character_list:
        for stat in stats_to_analyze:
            stat_for_all_chars = [getattr(i, stat) for i in characters]
            mean = statistics.mean(stat_for_all_chars)
            stdev = statistics.stdev(stat_for_all_chars)
            temp_dict = {"mean": mean, "stdev": stdev,
                         "full_list": stat_for_all_chars}
            stat_dict[stat] = temp_dict

    return stat_dict


def fight_random_characters(number_of_fights: int, character1: Character = None, character2: Character = None, complete_random=True) -> list:
    all_fights = []

    # check if characters assigned, else generate random characters
    if character1:
        character1 = character1
    else:
        character1 = create_character_easy("character")

    if character2:
        character2 = character2
    else:
        character2 = create_character_easy("create_character")

    for _ in range(number_of_fights):
        if complete_random == True:
            character1 = create_character_easy("character")
            character2 = create_character_easy("character")

        fight = fight_to_death(character1, character2)
        all_fights.append(fight)

    return all_fights


def extract_stat_df(characters: list) -> pd.DataFrame:
    stat_data = pd.DataFrame(columns=["character", "stat", "value"])
    all_stats = ["str", "dex", "con", "int", "wis", "cha"]
    for character in characters:
        for stat in all_stats:
            temp_df = pd.DataFrame(
                [[character, stat, eval("character.%s" % stat)]],
                columns=["character", "stat", "value"]
            )
            stat_data = stat_data.append(temp_df)

    stat_data["value"] = stat_data["value"].apply(pd.np.float64)
    stat_data["character"] = stat_data["character"].apply(str)
    stat_data["stat_rank"] = stat_data.groupby(
        "character")["value"].rank("dense", ascending=False)

    summarized_stat_data = pd.DataFrame(
        columns=["str", "dex", "con", "int", "wis", "cha"])
    mean = stat_data.groupby("stat")["value"].mean()
    mean.name = 'mean'
    rank = stat_data.groupby("stat")["stat_rank"].mean() + 1
    rank.name = 'avg rank'
    summarized_stat_data = summarized_stat_data.append(mean)
    summarized_stat_data = summarized_stat_data.append(rank)

    return summarized_stat_data
    # return stat_data
