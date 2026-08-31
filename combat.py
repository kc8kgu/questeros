"""Pure rules for random encounters and turn-based battles."""
import random

# sprite key is f"mon_{id}"; see graphics.monsters.MONSTER_LOOKS
MONSTERS = [
    dict(id="rat",      name="Giant Rat", hp=6,  atk=3,  dfn=0, gold=5,   xp=8,   min_level=1),
    dict(id="bat",      name="Cave Bat",  hp=8,  atk=4,  dfn=0, gold=8,   xp=12,  min_level=1),
    dict(id="goblin",   name="Goblin",    hp=12, atk=5,  dfn=1, gold=22,  xp=18,  min_level=1),
    dict(id="skeleton", name="Skeleton",  hp=16, atk=6,  dfn=2, gold=38,  xp=27,  min_level=2),
    dict(id="orc",      name="Orc",       hp=22, atk=8,  dfn=2, gold=60,  xp=45,  min_level=2),
    dict(id="ogre",     name="Ogre",      hp=32, atk=10, dfn=3, gold=105, xp=75,  min_level=3),
    dict(id="troll",    name="Troll",     hp=45, atk=13, dfn=4, gold=180, xp=135, min_level=4),
    dict(id="dragon",   name="Dragon",    hp=80, atk=18, dfn=6, gold=450, xp=375, min_level=6, boss=True),
]

ENCOUNTER_CHANCE = 0.08
RUN_CHANCE = 0.5

ACTION_ATTACK = "attack"
ACTION_EAT = "eat"
ACTION_RUN = "run"
ACTIONS = (ACTION_ATTACK, ACTION_EAT, ACTION_RUN)


def pick_monster(level):
    eligible = [
        m for m in MONSTERS
        if m["min_level"] <= level and not m.get("boss")
    ]
    return random.choice(eligible)


BOSS_MONSTER = next(monster for monster in MONSTERS if monster.get("boss"))


class Battle:
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster
        self.mhp = monster["hp"]
        self.log = [f"A {monster['name']} attacks!"]
        self.over = False
        self.result = None    # "won" | "fled" | "lost"

    def say(self, msg):
        self.log.append(msg)
        del self.log[:-3]

    # --- player actions; a failed action is free, a valid one costs a turn ---

    def act(self, action):
        if action == ACTION_ATTACK:
            self.player_attack()
        elif action == ACTION_EAT:
            self.player_eat()
        elif action == ACTION_RUN:
            self.player_run()
        else:
            raise ValueError(f"Unknown battle action: {action}")

    def player_attack(self):
        dmg = max(1, self.player.attack() + random.randint(-1, 2) - self.monster["dfn"])
        self.mhp -= dmg
        self.say(f"You hit the {self.monster['name']} for {dmg}!")
        if self.mhp <= 0:
            self.mhp = 0
            self.victory()
        else:
            self.monster_attack()

    def player_eat(self):
        healed, msg = self.player.eat_ration()
        self.say(msg)
        if healed:
            self.monster_attack()

    def player_run(self):
        if random.random() < RUN_CHANCE:
            self.say("You escape!")
            self.over = True
            self.result = "fled"
        else:
            self.say("You couldn't escape!")
            self.monster_attack()

    def monster_attack(self):
        p = self.player
        dmg = p.take_damage(max(
            1, self.monster["atk"] + random.randint(0, 2) - p.defense() - 1))
        if p.dead:
            self.over = True
            self.result = "lost"
            self.say(f"The {self.monster['name']} hits you for {dmg}! You die...")
        elif not dmg:
            self.say(f"The {self.monster['name']} cannot hurt you!")
        else:
            self.say(f"The {self.monster['name']} hits you for {dmg}!")

    def victory(self):
        p = self.player
        gold = self.monster["gold"] + random.randint(0, self.monster["gold"] // 2)
        p.gold += gold
        level_before = p.level
        p.gain_xp(self.monster["xp"])
        self.say(f"You defeated the {self.monster['name']}! +{gold}g +{self.monster['xp']}xp")
        if p.level > level_before:
            self.say(f"LEVEL UP! You are now level {p.level}.")
        self.over = True
        self.result = "won"
