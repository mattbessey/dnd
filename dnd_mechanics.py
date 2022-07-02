from dice_rollers import rollSixStats, findStatModifier, roll_dice


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

        # set attributes
        self.str = self.dex = self.con = self.int = self.wis = self.cha = 0

        # I don't actually know if this is good practice
        self.get_stat_mod = findStatModifier

    def set_stat(self, stat_to_modify: str, stat_number: int):
        setattr(self, stat_to_modify, stat_number)

    def set_hitpoints(self):
        # first level shouldn't have a roll
        con_mod = self.get_stat_mod(self.con)
        self.hitpoints = roll_dice(
            self.hit_die) + (con_mod * self.hit_die[0]) + self.hit_die[1]

    def get_attacked(self, attack_dictionary: dict):
        print(f"{self.name} gets attacked")
        if attack_dictionary["to_hit"] >= self.armor_class:
            print("it's a hit")
            self.take_damage(attack_dictionary["damage"])
        else:
            print("it's a miss")

    def take_damage(self, damage: int):
        if damage >= self.hitpoints:
            self.state = "dead"
        self.hitpoints -= damage

    def equip_weapon(self, weapon: Weapon):
        self.weapon = weapon

    def attack(self, attack_stat: int = "str"):
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
    character = create_character(
        name=name, stat_list=stat_list, stat_rank_order=stat_rank_order
    )
    katana = Weapon()
    character.equip_weapon(katana)

    return character


def fight_to_death(character1: Character, character2: Character):
    character1.roll_for_initiative()
    character2.roll_for_initiative()
    turn_count = 0

    if character1.initiative > character2.initiative:
        while character1.state == "alive" and character2.state == "alive":
            turn_count += 1
            character2.get_attacked(character1.attack())
            character1.get_attacked(character2.attack())

    elif character2.initiative > character1.initiative:
        while character1.state == "alive" and character2.state == "alive":
            turn_count += 1
            character1.get_attacked(character1.attack())
            character2.get_attacked(character2.attack())

    if character1.state == "alive":
        return [character1, turn_count]

    elif character2.state == "alive":
        return [character2, turn_count]
