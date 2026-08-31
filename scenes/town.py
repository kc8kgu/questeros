"""Town exploration, service menus, vendors, guards, and economy behavior."""
import items
import menus
import settings as s
import town
import town_crime
from casino import BET_AMOUNTS, CASINO_ALERT_GOLD, flip
from graphics.actors import GUARD, VENDOR
from graphics.ui import (
    ICON_ARMOR, ICON_CASINO, ICON_FOOD, ICON_GOLD, ICON_HP, ICON_LEAVE,
    ICON_REST, ICON_WEAPON,
)
from scenes.exploration import ExplorationScene


class MapActor:
    def __init__(self, sprite, x, y):
        self.sprite = sprite
        self.fx = float(x)
        self.fy = float(y)


class TownScene(ExplorationScene):
    def __init__(self, game, return_scene, town_x, town_y, return_pos):
        game_map, self.town_state = town.generate(town_x, town_y)
        super().__init__(game, game_map)
        self.return_scene = return_scene
        self.town_x = town_x
        self.town_y = town_y
        self.return_pos = return_pos
        self.casino_pot = 0
        self._pending_battle = None

        player = game.player
        player.x, player.y = town.SPAWN
        player.fx, player.fy = float(player.x), float(player.y)
        player.target = None

    def map_actors(self):
        actors = []
        for vendor in self.town_state.vendors:
            if vendor.alive:
                actors.append(MapActor(VENDOR, vendor.x, vendor.y))
        for guard in self.town_state.guards:
            if guard.alive:
                actors.append(MapActor(GUARD, guard.x, guard.y))
        return actors

    def on_arrive(self):
        player = self.game.player
        tile = self.game_map.tile_at(player.x, player.y)
        if tile == "gate":
            player.x, player.y = self.return_pos
            player.fx, player.fy = float(player.x), float(player.y)
            player.target = None
            self.game.change_scene(self.return_scene)
            return

        guard = town.guard_at(self.town_state, player.x, player.y)
        if guard and guard.hostile:
            self._start_guard_battle(guard)
            return

        vendor = town.vendor_at(self.town_state, player.x, player.y)
        if vendor:
            self.menu = self.build_vendor_menu(vendor)
            return

        if tile.startswith("counter_"):
            service = tile.removeprefix("counter_")
            vendor = town.vendor_for_service(self.town_state, service)
            if vendor and vendor.alive:
                self.menu = self._build_service_menu(service)

    def update(self, dt):
        if not self.menu and not self.inventory and not self._pending_battle:
            self._update_guards(dt)
            self._check_guard_collision()
        super().update(dt)

    def _update_guards(self, dt):
        for guard in self.town_state.guards:
            if not guard.alive:
                continue
            guard.step_timer += dt
            if guard.step_timer < s.GUARD_STEP_TIME:
                continue
            guard.step_timer = 0.0
            if guard.hostile:
                self._chase_player(guard)
            elif len(guard.route) > 1:
                guard.index = (guard.index + 1) % len(guard.route)
                guard.x, guard.y = guard.route[guard.index]
                guard.fx, guard.fy = float(guard.x), float(guard.y)

    def _chase_player(self, guard):
        player = self.game.player
        best = None
        best_dist = abs(guard.x - player.x) + abs(guard.y - player.y)
        for dx, dy in town.CARDINAL:
            nx, ny = guard.x + dx, guard.y + dy
            if not self.game_map.is_walkable(nx, ny):
                continue
            dist = abs(nx - player.x) + abs(ny - player.y)
            if dist < best_dist:
                best_dist = dist
                best = (nx, ny)
        if best:
            guard.x, guard.y = best
            guard.fx, guard.fy = float(best[0]), float(best[1])

    def _check_guard_collision(self):
        player = self.game.player
        if player.target:
            return
        guard = town.guard_at(self.town_state, player.x, player.y)
        if guard and guard.hostile:
            self._start_guard_battle(guard)

    def _alert_guards(self):
        self.town_state.alerted = True
        for guard in self.town_state.guards:
            guard.hostile = True

    def _start_guard_battle(self, guard):
        self._pending_battle = ("guard", guard)
        from scenes.battle import BattleScene

        self.game.change_scene(BattleScene(
            self.game, self, dict(town_crime.GUARD_MONSTER),
            terrain="tfloor", town_target=("guard", guard)))

    def _start_vendor_battle(self, vendor):
        self._pending_battle = ("vendor", vendor)
        from scenes.battle import BattleScene

        self.game.change_scene(BattleScene(
            self.game, self, dict(town_crime.VENDOR_MONSTER),
            terrain="tfloor", town_target=("vendor", vendor)))

    def resolve_town_battle(self, target_kind, target, result):
        self._pending_battle = None
        if result != "won":
            return
        if target_kind == "vendor":
            target.alive = False
            self._alert_guards()
        elif target_kind == "guard":
            target.alive = False
            if not any(
                    guard.alive and guard.hostile
                    for guard in self.town_state.guards):
                self.town_state.alerted = False

    def build_vendor_menu(self, vendor):
        menu = menus.Menu("vendor", "Vendor")
        menu.vendor = vendor
        menu.options = [
            ["Rob", not vendor.robbed],
            ["Fight", vendor.alive],
            ["Leave", True],
        ]
        menu.icons = [ICON_GOLD, ICON_WEAPON, ICON_LEAVE]
        return menu

    def vendor_selected(self, index):
        vendor = self.menu.vendor
        if index == 2:
            self.menu = None
            return
        if index == 0:
            if vendor.robbed:
                self.menu.set_status("Already robbed.", s.GREY)
                return
            gold = town_crime.rob_gold()
            self.game.player.gold += gold
            vendor.robbed = True
            self._alert_guards()
            self.menu.set_status(
                f"You stole {gold}g!  Gold: {self.game.player.gold}", s.LTRED)
            return
        self.menu = None
        self._start_vendor_battle(vendor)

    def _build_service_menu(self, service):
        builders = {
            "weapon": self.build_weapon_menu,
            "armor": self.build_armor_menu,
            "food": self.build_food_menu,
            "inn": self.build_inn_menu,
            "casino": self.build_casino_menu,
        }
        return builders[service]()

    def build_inn_menu(self):
        menu = menus.Menu("inn", "The Inn")
        menu.options = [
            [f"Rest — full HP  ({items.INN_REST}g)", True],
            [f"Meal — +{items.MEAL_FOOD} food  ({items.INN_MEAL}g)", True],
            [f"Feast — full HP & food  ({items.INN_FEAST}g)", True],
            ["Leave", True],
        ]
        menu.icons = [ICON_REST, ICON_FOOD, ICON_HP, ICON_LEAVE]
        menu.set_status(f"Gold: {self.game.player.gold}", s.YELLOW)
        return menu

    def inn_selected(self, index):
        player = self.game.player
        if index == 3:
            self.menu = None
            return
        price = (items.INN_REST, items.INN_MEAL, items.INN_FEAST)[index]
        if not player.spend(price):
            self.menu.set_status("Not enough gold!", s.LTRED)
            return
        if index == 0:
            player.hp = player.max_hp
            message = "You wake fully rested."
        elif index == 1:
            player.food = min(100, player.food + items.MEAL_FOOD)
            message = "A hearty meal."
        else:
            player.hp = player.max_hp
            player.food = 100
            message = "You feast like royalty!"
        self.menu.set_status(
            f"{message}  Gold: {player.gold}", s.LTGREEN)

    def _weapon_label(self, index):
        name, price, attack = items.WEAPONS[index]
        player = self.game.player
        if player.weapon == index:
            tag = "equipped"
        elif index in player.weapons_owned:
            tag = "owned"
        else:
            tag = f"{price}g"
        return f"{name}  ATK+{attack}  [{tag}]"

    def _armor_label(self, index):
        name, price, defense = items.ARMORS[index]
        player = self.game.player
        if player.armor == index:
            tag = "equipped"
        elif index in player.armors_owned:
            tag = "owned"
        else:
            tag = f"{price}g"
        return f"{name}  DEF+{defense}  [{tag}]"

    def build_weapon_menu(self):
        menu = menus.Menu("weapon", "Weapons")
        self._refresh_weapon_menu(menu)
        menu.set_status(f"Gold: {self.game.player.gold}", s.YELLOW)
        return menu

    def _refresh_weapon_menu(self, menu):
        menu.options = []
        menu.entries = []
        menu.icons = []
        for index in range(1, len(items.WEAPONS)):
            menu.options.append([self._weapon_label(index), True])
            menu.entries.append(index)
            menu.icons.append(ICON_WEAPON)
        menu.options.append(["Leave", True])
        menu.entries.append(None)
        menu.icons.append(ICON_LEAVE)

    def weapon_selected(self, index):
        if index == len(self.menu.entries) - 1:
            self.menu = None
            return
        weapon_index = self.menu.entries[index]
        player = self.game.player
        name, price, _ = items.WEAPONS[weapon_index]
        if weapon_index == player.weapon:
            self.menu.set_status("Already equipped.", s.GREY)
        elif weapon_index in player.weapons_owned:
            player.weapon = weapon_index
            self.menu.set_status(f"Equipped {name}.", s.LTGREEN)
        elif player.spend(price):
            player.weapons_owned.add(weapon_index)
            player.weapon = weapon_index
            self.menu.set_status(
                f"Bought {name}!  Gold: {player.gold}", s.LTGREEN)
        else:
            self.menu.set_status("Not enough gold!", s.LTRED)
        if self.menu:
            self._refresh_weapon_menu(self.menu)

    def build_armor_menu(self):
        menu = menus.Menu("armor", "Armor")
        self._refresh_armor_menu(menu)
        menu.set_status(f"Gold: {self.game.player.gold}", s.YELLOW)
        return menu

    def _refresh_armor_menu(self, menu):
        menu.options = []
        menu.entries = []
        menu.icons = []
        for index in range(1, len(items.ARMORS)):
            menu.options.append([self._armor_label(index), True])
            menu.entries.append(index)
            menu.icons.append(ICON_ARMOR)
        menu.options.append(["Leave", True])
        menu.entries.append(None)
        menu.icons.append(ICON_LEAVE)

    def armor_selected(self, index):
        if index == len(self.menu.entries) - 1:
            self.menu = None
            return
        armor_index = self.menu.entries[index]
        player = self.game.player
        name, price, _ = items.ARMORS[armor_index]
        if armor_index == player.armor:
            self.menu.set_status("Already equipped.", s.GREY)
        elif armor_index in player.armors_owned:
            player.armor = armor_index
            self.menu.set_status(f"Equipped {name}.", s.LTGREEN)
        elif player.spend(price):
            player.armors_owned.add(armor_index)
            player.armor = armor_index
            self.menu.set_status(
                f"Bought {name}!  Gold: {player.gold}", s.LTGREEN)
        else:
            self.menu.set_status("Not enough gold!", s.LTRED)
        if self.menu:
            self._refresh_armor_menu(self.menu)

    def build_food_menu(self):
        menu = menus.Menu("food", "Food")
        menu.options = [
            [f"Rations +{items.RATION_FOOD} food  ({items.RATION_PRICE}g)",
             True],
            ["Leave", True],
        ]
        menu.icons = [ICON_FOOD, ICON_LEAVE]
        menu.set_status(f"Gold: {self.game.player.gold}", s.YELLOW)
        return menu

    def food_selected(self, index):
        player = self.game.player
        if index == 1:
            self.menu = None
            return
        if player.spend(items.RATION_PRICE):
            player.food = min(100, player.food + items.RATION_FOOD)
            self.menu.set_status(
                f"Food +{items.RATION_FOOD}!  Gold: {player.gold}",
                s.LTGREEN)
        else:
            self.menu.set_status("Not enough gold!", s.LTRED)

    def build_casino_menu(self):
        if self.casino_pot > 0:
            return self._build_casino_risk_menu()
        menu = menus.Menu("casino", "Casino")
        menu.options = []
        menu.entries = []
        menu.icons = []
        for amount in BET_AMOUNTS:
            affordable = self.game.player.gold >= amount
            menu.options.append([f"Bet {amount}g", affordable])
            menu.entries.append(amount)
            menu.icons.append(ICON_GOLD)
        menu.options.append(["Leave", True])
        menu.entries.append(None)
        menu.icons.append(ICON_LEAVE)
        menu.set_status(f"Gold: {self.game.player.gold}", s.YELLOW)
        return menu

    def _build_casino_risk_menu(self):
        menu = menus.Menu("casino", "Casino")
        pot = self.casino_pot
        menu.options = [
            [f"Risk {pot}g to win {pot * 2}g", True],
            [f"Take {pot}g", True],
            ["Leave", True],
        ]
        menu.icons = [ICON_CASINO, ICON_GOLD, ICON_LEAVE]
        menu.set_status(f"Winnings at risk: {pot}g", s.LTGREEN)
        return menu

    def casino_selected(self, index):
        if self.casino_pot > 0:
            self._casino_risk_selected(index)
            return
        if index == len(self.menu.entries) - 1:
            self.menu = None
            return
        amount = self.menu.entries[index]
        player = self.game.player
        if not player.spend(amount):
            self.menu.set_status("Not enough gold!", s.LTRED)
            return
        self.casino_pot = amount
        self._resolve_casino_flip(double_on_win=False)

    def _casino_risk_selected(self, index):
        if index == 2:
            self.casino_pot = 0
            self.menu = None
            return
        if index == 1:
            winnings = self.casino_pot
            self.game.player.gold += winnings
            if winnings >= CASINO_ALERT_GOLD:
                self._alert_guards()
            self.casino_pot = 0
            self.menu = self.build_casino_menu()
            self.menu.set_status(
                f"You take {winnings}g!  Gold: {self.game.player.gold}",
                s.LTGREEN)
            return
        self._resolve_casino_flip(double_on_win=True)

    def _resolve_casino_flip(self, double_on_win=False):
        player = self.game.player
        if flip():
            if double_on_win:
                self.casino_pot *= 2
            self.menu = self._build_casino_risk_menu()
            self.menu.set_status(
                f"You won!  {self.casino_pot}g at risk.", s.LTGREEN)
            return
        lost = self.casino_pot
        self.casino_pot = 0
        self.menu = self.build_casino_menu()
        self.menu.set_status(
            f"You lost {lost}g.  Gold: {player.gold}", s.LTRED)

    def menu_selected(self):
        index = self.menu.selected
        dispatch = {
            "vendor": self.vendor_selected,
            "inn": self.inn_selected,
            "weapon": self.weapon_selected,
            "armor": self.armor_selected,
            "food": self.food_selected,
            "casino": self.casino_selected,
        }
        dispatch[self.menu.kind](index)
