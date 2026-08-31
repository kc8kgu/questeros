"""The player: grid movement state, stats, and inventory."""
import items
import settings as s

FOOD_STEP_INTERVAL = 20    # steps taken per point of food consumed
STARVE_STEP_INTERVAL = 10  # steps taken per HP lost while out of food
XP_PER_LEVEL = 100


class Player:
    def __init__(self, x, y, god_mode=False):
        # position and movement
        self.x, self.y = x, y
        self.fx, self.fy = float(x), float(y)
        self.last_pos = (x, y)
        self.target = None
        self.t = 0.0
        self.facing = "down"
        self.just_arrived = False

        # stats
        self.max_hp = 50
        self.hp = 50
        self.gold = 100
        self.food = 100
        self.level = 1
        self.xp = 0
        self.steps = 0
        self.dead = False
        self.invincible = False
        self._normal_stats = None
        self._since_food = 0
        self._since_starve = 0

        # inventory: indices into items.WEAPONS / items.ARMORS
        self.weapon = 0
        self.armor = 0
        self.weapons_owned = {0}
        self.armors_owned = {0}

        if god_mode:
            self.toggle_god_mode()

    # --- movement -----------------------------------------------------------

    def try_step(self, dx, dy, game_map):
        if self.target:
            return
        if dx:
            self.facing = "right" if dx > 0 else "left"
        if dy:
            self.facing = "down" if dy > 0 else "up"
        tx, ty = self.x + dx, self.y + dy
        if game_map.is_walkable(tx, ty):
            self.target = (tx, ty)
            self.t = 0.0

    def update(self, dt):
        if not self.target:
            return
        self.t += dt / s.STEP_TIME
        if self.t >= 1.0:
            self.last_pos = (self.x, self.y)
            self.x, self.y = self.target
            self.fx, self.fy = float(self.x), float(self.y)
            self.target = None
            self.just_arrived = True
            self.on_arrive()
        else:
            tx, ty = self.target
            self.fx = self.x + (tx - self.x) * self.t
            self.fy = self.y + (ty - self.y) * self.t

    # --- combat-relevant numbers ---------------------------------------------

    def attack(self):
        return 2 + self.level + items.WEAPONS[self.weapon][2]

    def defense(self):
        return items.ARMORS[self.armor][2]

    # --- stats --------------------------------------------------------------

    def spend(self, amount):
        if self.invincible:
            return True
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def eat_ration(self):
        """Eat a ration. Returns (healed_hp, message); healed is 0 when unable."""
        if self.hp >= self.max_hp:
            return 0, "You are already at full health."
        if self.food < s.EAT_FOOD_COST:
            return 0, "Not enough food!"
        healed = min(s.EAT_HEAL, self.max_hp - self.hp)
        self.food -= s.EAT_FOOD_COST
        self.hp += healed
        return healed, f"You eat a ration and recover {healed} HP."

    def take_damage(self, amount):
        if self.invincible:
            return 0
        damage = min(self.hp, amount)
        self.hp -= damage
        if self.hp == 0:
            self.dead = True
        return damage

    def toggle_god_mode(self):
        if self.invincible:
            self.max_hp, self.hp, self.gold = self._normal_stats
            self._normal_stats = None
            self.invincible = False
        else:
            self._normal_stats = self.max_hp, self.hp, self.gold
            self.max_hp = 1000
            self.hp = 1000
            self.gold = 1000
            self.invincible = True

    def on_arrive(self):
        """Called each time a step onto a new tile completes."""
        self.steps += 1
        if self.food > 0:
            self._since_food += 1
            if self._since_food >= FOOD_STEP_INTERVAL:
                self._since_food = 0
                self.food -= 1
        else:
            self._since_starve += 1
            if self._since_starve >= STARVE_STEP_INTERVAL:
                self._since_starve = 0
                self.take_damage(1)

    def xp_needed(self):
        return XP_PER_LEVEL * self.level

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_needed():
            self.xp -= self.xp_needed()
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp  # leveling up fully heals
