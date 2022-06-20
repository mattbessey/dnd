We're going to explore ML languages through games.
Games have defined rules and can be either deterministic or semi-deterministic with some randomized inputs.
* Will removing the random qualities affect the analysis?

# DnD
First approach will be to optimize the stat assignment of a DnD character.
To begin we will have the following constraints:
* We will focus on level 1 characters
* Items & abilities will be removed (to add later?)
* Melee-only
* Assume fighter class (adding add'l melee classes would be a good next step)
* We will randomize stats with 4d6 drop lowest

Under these constraints we should see:
* Stats should be optimized towards str/dex/con, as those are the only stats that should matter in melee
* Will the difference matter if the HP die is rolled before the the stats are assigned?